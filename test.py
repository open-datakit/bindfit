import test
import unittest
import test_helpers
import numpy as np
import pandas as pd
import pprint

class TestBindfit(unittest.TestCase):
    # Test nmr1to1 fitter with Nelder-Mead method
    def test_nmr_1to1(self):
        input_file = "NMR1to1.csv"
        hostname = "Host"
        guestname = "Guest"
        fitter_name = "nmr1to1"
        method = "Nelder-Mead"
        normalise = True
        dilute = False
        flavour = "none"
        params = {
        "k": {
                "init": 100.0,
                "bounds": {
                    "min": 0.0,
                    "max": None,
                },
            },
        }

        summary = test_helpers.run_bindfit(input_file, hostname, guestname, fitter_name, method, normalise, flavour, params)

        #K = 334 +/- 2.5
        test_helpers.assertValueInRange(self, summary.get("k").get("value"), 334, 2.5)

    def test_nmr_1to2(self):
        input_file = "NMR1to2.csv"
        hostname = "Host"
        guestname = "Guest"
        fitter_name = "nmr1to2"
        method = "Nelder-Mead"
        normalise = True
        dilute = False
        flavour = "none"
        params = {
            "k11": {
                    "init": 100.0,
                    "bounds": {
                        "min": 0.0,
                        "max": None,
                    },
                },
            "k12": {
                "init": 100.0,
                "bounds": {
                    "min": 0.0,
                    "max": None,
                },
            },
        }

        summary = test_helpers.run_bindfit(input_file, hostname, guestname, fitter_name, method, normalise, flavour, params)

        #K11 = 13503 +/- 25
        #K12 = 413 +/- 15
        test_helpers.assertValueInRange(self, summary.get("k11").get("value"), 13503, 25)
        test_helpers.assertValueInRange(self, summary.get("k12").get("value"), 413, 15)

if __name__ == '__main__':
    unittest.main()