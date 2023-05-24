#!/usr/bin/env python

import numpy as np

from bindfit import functions, fitter, formatter

params = {
    "k": {
        "init": 100.0,
        "bounds": {
            "min": 0.0,
            "max": None,
        }
    }
}

data = np.genfromtxt("input.csv", delimiter=",", skip_header=1)

# Bindfit expects each variable as rows
data_x = np.transpose(data[:, :2])
data_y = np.transpose(data[:, 2:])

function = functions.construct(
    "nmr1to1",
    normalise=True,
    flavour="none",
)

fitter = fitter.Fitter(
    data_x,
    data_y,
    function,
    normalise=True,
    params=params
)

fitter.run_scipy(
    params,
    method="Nelder-Mead"
)

response = formatter.fit(
    fitter="nmr1to1",
    data={
        "data": {
            "x": data_x,
            "y": data_y,
        },
    },
    y=fitter.fit,
    params=fitter.params,
    residuals=fitter.residuals,
    coeffs_raw=fitter.coeffs_raw,
    molefrac_raw=fitter.molefrac_raw,
    coeffs=fitter.coeffs,
    molefrac=fitter.molefrac,
    time=fitter.time,
    dilute=False,
    normalise=True,
    method="Nelder-Mead",
    flavour="none",
)

import pprint
pprint.pprint(response)
