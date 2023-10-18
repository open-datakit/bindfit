#!/usr/bin/env python


import json

import bindfit


with open("input.json", "r") as f:
    datapackage = json.load(f)

bindfit.datapackage.fit(datapackage["datapackage"])
