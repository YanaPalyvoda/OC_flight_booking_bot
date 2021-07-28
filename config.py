#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")#"ccf0278f-683e-4226-9479-223ca207115d")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")#"EB9.IjS&wW]B$yEHWq.5(*&GErn:ZNMk")
    LUIS_APP_ID = os.environ.get("LuisAppId", "383654ee-9960-452f-b581-6866c829cd9b")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "74485270f887423aa297c00418cf0f57")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "westeurope.api.cognitive.microsoft.com")
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get("InstrumentationKey","7d6dcbc4-61b9-4d90-b6b4-b68c9cf80676")
