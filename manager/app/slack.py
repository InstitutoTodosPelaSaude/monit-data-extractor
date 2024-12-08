import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def get_slack_client():
    client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])
    return client