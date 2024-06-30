# -*- coding: utf-8 -*-
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    ApiClient, Configuration, MessagingApi,
    ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import (
    FollowEvent, MessageEvent, TextMessageContent
)
import os

# Load .env file
from dotenv import load_dotenv
load_dotenv()

# Assign environment variables to variables
CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

# Instantiate Flask app
app = Flask(__name__)

# Load LINE access token
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# Callback function
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# Send a message when a friend is added
@handler.add(FollowEvent)
def handle_follow(event):
    # Instantiate API client
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        # Reply
        line_bot_api.reply_message(ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text='Thank You!')]
        ))

# Echo back received messages
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    # Instantiate API client
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        # Get the content of the received message
        received_message = event.message.text

        # Call API to get sender's profile
        profile = line_bot_api.get_profile(event.source.user_id)
        display_name = profile.display_name

        # Edit reply message
        reply = f'{display_name}, you said:\n{received_message}'

        # Echo back
        line_bot_api.reply_message(ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply)]
        ))

# Top page for checking if the bot is running
@app.route('/', methods=['GET'])
def toppage():
    return 'Hello world!'

# Bot startup code
if __name__ == "__main__":
    # Set `debug=True` for local testing
    app.run(host="0.0.0.0", port=8000, debug=True)

