#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "0604577f-6035-4e38-bf90-4b022c0f025a")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "P@risismagical21")

    #APP_ID = os.environ.get("MicrosoftAppId", "")
    #APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

    LUIS_APP_ID = os.environ.get("LuisAppId", "fa4cfa08-373d-4c8d-84fd-3423d3e8814c")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "6faee2d4ebfc40f7a51c549d67e0f60c")
    # LUIS endpoint host name, ie "https://westeurope.api.cognitive.microsoft.com/"
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "westeurope.api.cognitive.microsoft.com")
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        "AppInsightsInstrumentationKey", "ddd0b4c5-5455-4889-9310-098ae3050143"
    )

    #https://docs.microsoft.com/en-us/azure/bot-service/bot-builder-deploy-az-cli?view=azure-bot-service-4.0&tabs=python