#!/usr/bin/env python

import numpy as np

import bindfit

import pprint


# Parameters and options
params = {
    "k": {
        "init": 100.0,
        "bounds": {
            "min": 0.0,
            "max": None,
        },
    },
}

fitter_name = "nmr1to1"
method = "Nelder-Mead"
normalise = True
dilute = False
flavour = "none"

# Load raw data
data = np.genfromtxt("input.csv", delimiter=",", skip_header=1)
# Bindfit expects each variable as rows
data_x = np.transpose(data[:, :2])
data_y = np.transpose(data[:, 2:])

# Apply dilution correction
# TODO: Think about where this should go - fitter or function?
# Or just apply it before the fit?
if dilute:
    data_y = bindfit.helpers.dilute(data_x[0], data_y)

function = bindfit.functions.construct(
    fitter_name,
    normalise=normalise,
    flavour=flavour,
)

fitter = bindfit.fitter.Fitter(
    data_x, data_y, function=function, normalise=normalise, params=params
)

fitter.run_scipy(params, method=method)

summary = {
    "fitter": fitter_name,
    "fit": {
        "y": fitter.fit,
        "coeffs_raw": fitter.coeffs_raw,
        "coeffs": fitter.coeffs,
        "molefrac_raw": fitter.molefrac_raw,
        "molefrac": fitter.molefrac,
        "params": fitter.params,
        "n_y": np.array(fitter.fit).size,
        "n_params": len(fitter.params) + np.array(fitter.coeffs_raw).size,
    },
    "qof": {
        "residuals": fitter.residuals,
        "ssr": bindfit.helpers.ssr(fitter.residuals),
        "rms": bindfit.helpers.rms(fitter.residuals),
        "cov": bindfit.helpers.cov(data_y, fitter.residuals),
        "rms_total": bindfit.helpers.rms(fitter.residuals, total=True),
        "cov_total": bindfit.helpers.cov(data_y, fitter.residuals, total=True),
    },
    "time": fitter.time,
    "options": {
        "dilute": dilute,
        "normalise": normalise,
        "method": method,
        "flavour": flavour,
    },
}

pprint.pprint(summary)
