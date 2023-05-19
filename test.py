#!/usr/bin/env python

import numpy as np

params = {
    "k": {
        "init": 100.0,
        "bounds": {
            "min": 0.0,
            "max": None,
        }
    }
}

data = np.genfromtxt("input.csv", delimiter=",")

print(data)

# function = functions.construct(
#     "nmr1to1",
#     normalise=True,
#     flavour="none",
# )
# 
# fitter = Fitter(
#     datax,
#     datay,
#     function,
#     normalise=True,
#     params=params
# )
