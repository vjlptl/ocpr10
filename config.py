#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    LUIS_APP_ID = os.environ.get("LuisAppId", "fa4cfa08-373d-4c8d-84fd-3423d3e8814c")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "6faee2d4ebfc40f7a51c549d67e0f60c")
    # LUIS endpoint host name, ie "https://westeurope.api.cognitive.microsoft.com/"
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "westeurope.api.cognitive.microsoft.com")
