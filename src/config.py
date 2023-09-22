"""This module imports user configuration settings from config.json and store them as constants."""
# pylint: disable=unspecified-encoding

import json


# Local files
with open("../config.json", "rt") as f:
    settings = json.load(f)


# Language and respective strings
LANGUAGE = settings["settings"]["language"]
CTB_LANGUAGE = "en" if LANGUAGE == "en" else "zh-hant" if LANGUAGE == "tc" else "zh-hans"

with open("../language_strings.json", "rt") as f:
    STRINGS = json.load(f)[LANGUAGE]


# Endpoints
KMB_ENDPOINT = settings["settings"]["kmb_endpoint"]
CTB_ENDPOINT = settings["settings"]["ctb_endpoint"]
CTB_BATCH_ROUTE_ENDPOINT = settings["settings"]["ctb_batch_route_endpoint"]
CTB_BATCH_ETA_ENDPOINT = settings["settings"]["ctb_batch_eta_endpoint"]


# Other constants
REQUEST_TIMEOUT_SECS = 15
