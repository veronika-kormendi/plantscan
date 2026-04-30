import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
# from dotenv import load_dotenv
# load_dotenv()
# SLACK_BOT_TOKEN = os.getenv('SLACK_API_TOKEN')
# SLACK_CHANNEL_ID = os.getenv('SLACK_CHANNEL_ID')
from config_refactor import SLACK_BOT_TOKEN, SLACK_CHANNEL_ID

# def send_slack_message(message, channel_id):
#     # client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
#     client = WebClient(token=SLACK_BOT_TOKEN)
#     try:
#         # response = client.chat_postMessage(channel=channel_id, text=message)
#         response = client.chat_postMessage(channel=SLACK_CHANNEL_ID, text=message)
#         return response["ok"]
#     except SlackApiError as e:
#         print(f" Slack error: {e.response['error']}")
#         return False


def test_slack():
    client = WebClient(token=SLACK_BOT_TOKEN)

    response = client.chat_postMessage(
        channel=SLACK_CHANNEL_ID,
        text="test messaging - Hello from PlantScan!"
    )

    print(response)

test_slack()