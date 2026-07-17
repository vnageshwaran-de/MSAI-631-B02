#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os


class DefaultConfig:
    """Bot configuration."""

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

    # --- MSAI-631 modification -------------------------------------------
    # Added for the Azure AI Language (Text Analytics) integration.
    # Values come from environment variables so the API key never lives in
    # source code. Set them before starting the bot, e.g. on Windows:
    #   SET MicrosoftAPIKey=<key 1 from Keys and Endpoint>
    #   SET MicrosoftAIServiceEndpoint=https://<resource>.cognitiveservices.azure.com/
    # or on macOS/Linux:
    #   export MicrosoftAPIKey=...
    #   export MicrosoftAIServiceEndpoint=...
    # ----------------------------------------------------------------------
    API_KEY = os.environ.get("MicrosoftAPIKey", "")
    ENDPOINT_URI = os.environ.get("MicrosoftAIServiceEndpoint", "")
