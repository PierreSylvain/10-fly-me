#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

import os


class DefaultConfig:
    """Configuration for the bot."""

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "7ff0aa79-e256-4375-a39c-d0aeb166c51e")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "-(Ia:z98=JHyNv=UwL>*Z]2h8h&")
    LUIS_APP_ID = os.environ.get("LuisAppId", "4d592d65-9c86-4987-a131-c73f66f26f55")
    LUIS_API_KEY = os.environ.get("LuisAPIKey", "06517d0c606c4cafb0ab434f6ff14bfc")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    LUIS_API_HOST_NAME = os.environ.get("LuisAPIHostName", "westeurope.api.cognitive.microsoft.com")
    APPINSIGHTS_INSTRUMENTATION_KEY = os.environ.get(
        "AppInsightsInstrumentationKey", "45a3aaf4-5a53-44da-9235-b9b5bec65469"
    )
    APPINSIGHTS_INSTRUMENTATION = os.environ.get(
        "AppInsightsInstrumentationCnx", "InstrumentationKey=45a3aaf4-5a53-44da-9235-b9b5bec65469;IngestionEndpoint=https://centralus-0.in.applicationinsights.azure.com/"
    )
