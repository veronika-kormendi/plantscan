from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config_refactor import SLACK_BOT_TOKEN, SLACK_CHANNEL_ID
import datetime

def send_slack_message(message, channel_id):
    client = WebClient(token=SLACK_BOT_TOKEN)
    timestamp = datetime.datetime.now().strftime("date: %Y-%m-%d time: %H:%M:%S")

    message_with_timestamp = f"{message} message was sent at {timestamp}"
    try:
        # response = client.chat_postMessage(channel=channel_id, text=message)
        response = client.chat_postMessage(channel=channel_id, text=message_with_timestamp)
        return response["ok"]
    except SlackApiError as e:
        print(f" Slack error: {e.response['error']}")
        return False

# only for testing
# def test_slack():
#     client = WebClient(token=SLACK_BOT_TOKEN)
#
#     response = client.chat_postMessage(
#         channel=SLACK_CHANNEL_ID,
#         text="test messaging - Hello from PlantScan!"
#     )
#
#     print(response)
#
# test_slack()