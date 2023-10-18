"""opendata.fit datapackage fitting helper functions"""

# TODO: Helper functions should be split out into own library eventually


import pandas as pd
import numpy as np

from . import helpers, functions
from .fitter import Fitter


# Model coefficients map
MODEL_COEFFS_MAP = {
    "nmr1to1": ["H", "HG"],
    "nmr1to2": ["H", "HG", "HG2"],
}


def find(array, key, value):
    """Equivalent of JS find() helper"""
    for i in array:
        if i[key] == value:
            return i

    return None


def find_by_name(array, name):
    return find(array, "name", name)


def get_algorithm_io_resource(datapackage, algorithm_name, io_type, io_name):
    """Get an algorithm input resource by name

    Parameters
    ----------
    datapackage: `dict`
        Bindfit datapackage object
    algorithm: `string`
        Name of algorithm
    io_type: `string` - "input" | "output"
        Whether to return an input or output resource
    input_name: `string`
        Name of input/output to return

    Returns
    -------
    resource: `dict` or `dict of dicts` or None
        Resource object, dict of resource objects or None if no matching
        resources
    """
    algorithm = find_by_name(datapackage["algorithms"], algorithm_name)
    resource = find_by_name(algorithm[io_type + "s"], io_name)["resource"]

    if isinstance(resource, str):
        return find_by_name(datapackage["resources"], resource)
    elif isinstance(resource, dict):
        return {
            key: find_by_name(datapackage["resources"], r)
            for key, r in resource.items()
        }


def tabular_data_resource_to_dataframe(resource):
    """Convert Frictionless tabular data resource to pandas DataFrame"""
    df = pd.DataFrame.from_dict(resource["data"])
    # Reorder columns by schema field order
    cols = [field["name"] for field in resource["schema"]["fields"]]
    df = df[cols]
    return df


def fit_to_json(data_resource, fit):
    """Convert Bindfit fit curve array to JSON format

    Convert fit curve array to JSON format for use in Frictionless tabular
    data. Add in independent variables.
    """
    x_fields = [i["name"] for i in data_resource["schema"]["fields"][:2]]
    y_fields = [i["name"] for i in data_resource["schema"]["fields"][2:]]

    fit_data = []

    for data_row, fit_row in zip(data_resource["data"], fit.T):
        row = {}

        for field in x_fields:
            row[field] = data_row[field]

        for i, field in enumerate(y_fields):
            row[field] = fit_row[i]

        fit_data.append(row)

    return fit_data


def molefracs_to_json(data_resource, molefracs, model):
    """Convert Bindfit molefractions array to JSON format

    Convert molefractions array to JSON format for use in Frictionless tabular
    data. Add in independent variables. Populate and return schema.
    """
    x_fields = [i["name"] for i in data_resource["schema"]["fields"][:2]]
    y_fields = MODEL_COEFFS_MAP[model]

    molefrac_data = []

    for data_row, molefrac_row in zip(data_resource["data"], molefracs.T):
        row = {}

        for field in x_fields:
            row[field] = data_row[field]

        for i, field in enumerate(y_fields):
            row[field] = molefrac_row[i]

        molefrac_data.append(row)

    molefrac_schema = {
        "primaryKey": data_resource["schema"]["primaryKey"],
        "fields": data_resource["schema"]["fields"][:2]
        + [
            {
                "name": i,
                "title": i,
                "type": "number",
                "unit": "",
            }
            for i in y_fields
        ],
    }

    return {
        "data": molefrac_data,
        "schema": molefrac_schema,
    }


def fit(datapackage):
    """Construct and run a Bindfit fitter from an opendata.fit datapackage

    Parameters
    ----------
    datapackage: `dict`
        Bindfit datapackage object

    Returns
    -------
    fitter: `bindfit.fitter.Fitter`
        Bindfit library fitter object
    """
    datapackage_data = get_algorithm_io_resource(
        datapackage, "bindfit", "input", "data"
    )
    datapackage_params = get_algorithm_io_resource(
        datapackage, "bindfit", "input", "params"
    )

    # Convert params to Bindfit format
    params = {}
    for key, param in datapackage_params["params"]["data"].items():
        params.update(
            {
                key: {
                    "init": param["value"],
                    "bounds": {
                        "min": param.get("lowerBound", None),
                        "max": param.get("upperBound", None),
                    },
                }
            }
        )

    # Get Bindfit options
    model = datapackage_params["params"]["metadata"]["model"]["name"]
    flavour = datapackage_params["params"]["metadata"]["model"].get(
        "flavour", None
    )
    method = datapackage_params["options"]["data"]["method"]["name"]
    normalise = datapackage_params["options"]["data"]["normalise"]
    dilute = datapackage_params["options"]["data"]["dilute"]

    df = tabular_data_resource_to_dataframe(datapackage_data)

    # Bindfit expects each variable as rows
    data_x = np.transpose(df.iloc[:, :2].to_numpy())
    data_y = np.transpose(df.iloc[:, 2:].to_numpy())

    # Apply dilution correction
    # TODO: Think about where this should go - fitter or function?
    # Or just apply it before the fit?
    if dilute:
        data_y = helpers.dilute(data_x[0], data_y)

    # Construct and run Bindfit fitter
    function = functions.construct(
        model,
        normalise=normalise,
        flavour=flavour,
    )

    fitter = Fitter(
        data_x, data_y, function, normalise=normalise, params=params
    )

    fitter.run_scipy(params, method=method)

    # Populate datapackage outputs
    datapackage_output_params = get_algorithm_io_resource(
        datapackage, "bindfit", "output", "params"
    )
    datapackage_output_fit = get_algorithm_io_resource(
        datapackage, "bindfit", "output", "fit"
    )
    datapackage_output_residuals = get_algorithm_io_resource(
        datapackage, "bindfit", "output", "residuals"
    )
    datapackage_output_molefracs = get_algorithm_io_resource(
        datapackage, "bindfit", "output", "molefracs"
    )
    datapackage_output_fit_details = get_algorithm_io_resource(
        datapackage, "bindfit", "output", "fitDetails"
    )
    datapackage_output_qof = get_algorithm_io_resource(
        datapackage, "bindfit", "output", "qof"
    )
    datapackage_output_coeffs = get_algorithm_io_resource(
        datapackage, "bindfit", "output", "coeffs"
    )

    # Populate params outputs
    for key, param in fitter.params.items():
        try:
            datapackage_output_params["data"].update(
                {
                    key: {
                        "value": param["value"],
                        "stderr": param["stderr"],
                    },
                }
            )
        except KeyError:
            # No existing data key, create
            datapackage_output_params = {
                "data": {
                    key: {
                        "value": param["value"],
                        "stderr": param["stderr"],
                    },
                },
            }

    # Populate output params schema and metadata from input params
    # TODO: Think of a better way of doing this?
    datapackage_output_params["metadata"] = datapackage_params["params"][
        "metadata"
    ]
    datapackage_output_params["schema"] = datapackage_params["params"][
        "schema"
    ]

    # Populate output fit curve
    datapackage_output_fit["data"] = fit_to_json(datapackage_data, fitter.fit)
    datapackage_output_fit["schema"] = datapackage_data["schema"]

    # Populate output residuals curve
    datapackage_output_residuals["data"] = fit_to_json(
        datapackage_data, fitter.fit - data_y
    )
    datapackage_output_residuals["schema"] = datapackage_data["schema"]

    # Populate output molefractions
    datapackage_output_molefracs.update(
        molefracs_to_json(datapackage_data, fitter.molefrac, model)
    )

    # Populate output fit details
    datapackage_output_fit_details["data"] = [
        {
            "time": fitter.time,
            "ssr": helpers.ssr(fitter.residuals),
            "n_y": np.array(fitter.fit).size,
            "n_params": len(fitter.params) + np.array(fitter.coeffs_raw).size,
        }
    ]

    # Populate output QoF
    # TODO: Output data should be stripped before being passed to algorithm
    # so we don't have to reset it beforehand
    datapackage_output_qof["data"] = []

    y_names = [i["name"] for i in datapackage_data["schema"]["fields"][2:]]
    rms = helpers.rms(fitter.residuals)
    cov = helpers.cov(data_y, fitter.residuals)
    for name, r, c in zip(y_names, rms, cov):
        datapackage_output_qof["data"].append(
            {
                "name": name,
                "rms": r,
                "cov": c,
            }
        )

    datapackage_output_qof["data"].append(
        {
            "name": "Total",
            "rms": helpers.rms(fitter.residuals, total=True),
            "cov": helpers.cov(data_y, fitter.residuals, total=True),
        }
    )

    # Populate output coefficients
    # TODO: Output data should be stripped before being passed to algorithm
    # so we don't have to reset it beforehand
    datapackage_output_coeffs["data"] = []

    y_names = [i["name"] for i in datapackage_data["schema"]["fields"][2:]]
    coeff_fields = MODEL_COEFFS_MAP[model]

    datapackage_output_coeffs["schema"] = {
        "primaryKey": "name",
        "fields": [
            {
                "name": "name",
                "title": "Name",
                "type": "string",
                "unit": "",
            }
        ]
        + [
            {
                "name": i,
                "title": i,
                "type": "number",
                "unit": "",
            }
            for i in coeff_fields
        ],
    }

    for name, c in zip(y_names, zip(*fitter.coeffs)):
        coeff_row = {"name": name, **dict(zip(coeff_fields, c))}

        datapackage_output_coeffs["data"].append(coeff_row)

    return {
        "params": datapackage_output_params,
        "fit": datapackage_output_fit,
        "residuals": datapackage_output_residuals,
        "molefracs": datapackage_output_molefracs,
        "fitDetails": datapackage_output_fit_details,
        "qof": datapackage_output_qof,
        "coeffs": datapackage_output_coeffs,
    }
