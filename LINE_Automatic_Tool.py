# -*- coding: utf-8 -*-
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
	ApiClient, Configuration, MessagingApi,
	ReplyMessageRequest, PushMessageRequest,
	TextMessage, PostbackAction
)
from linebot.v3.webhooks import (
	FollowEvent, MessageEvent, PostbackEvent, TextMessageContent
)
import os

## .env �t�@�C���ǂݍ���
from dotenv import load_dotenv
load_dotenv()

## ���ϐ���ϐ��Ɋ��蓖��
CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

**/.DS_Store  ## �s�v�ȊǗ��t�@�C���̏��O
**/__pycache__  ## �L���b�V���t�@�C���̏��O
.env  ## ���ϐ��t�@�C��
venv  ## ���z��

## Flask �A�v���̃C���X�^���X��
app = Flask(__name__)

## LINE �̃A�N�Z�X�g�[�N���ǂݍ���
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

## �R�[���o�b�N�̂��܂��Ȃ�
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

## �F�B�ǉ����̃��b�Z�[�W���M
@handler.add(FollowEvent)
def handle_follow(event):
	## API�C���X�^���X��
	with ApiClient(configuration) as api_client:
		line_bot_api = MessagingApi(api_client)

	## �ԐM
	line_bot_api.reply_message(ReplyMessageRequest(
		replyToken=event.reply_token,
		messages=[TextMessage(text='Thank You!')]
	))
## �I�E���Ԃ����b�Z�[�W
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
	## API�C���X�^���X��
	with ApiClient(configuration) as api_client:
		line_bot_api = MessagingApi(api_client)

	## ��M���b�Z�[�W�̒��g���擾
	received_message = event.message.text

	## API���Ă�ő��M�҂̃v���t�B�[���擾
	profile = line_bot_api.get_profile(event.source.user_id)
	display_name = profile.display_name

	## �ԐM���b�Z�[�W�ҏW
	reply = f'{display_name}����̃��b�Z�[�W\n{received_message}'

	## �I�E���Ԃ�
	line_bot_api.reply_message(ReplyMessageRequest(
		replyToken=event.reply_token,
		messages=[TextMessage(text=reply)]
	))
## �{�b�g�N���R�[�h
if __name__ == "__main__":
	## ���[�J���Ńe�X�g���鎞�̂��߂ɁA`debug=True` �ɂ��Ă���
	app.run(host="0.0.0.0", port=8000, debug=True)
	
	## �N���m�F�p�E�F�u�T�C�g�̃g�b�v�y�[�W
@app.route('/', methods=['GET'])
def toppage():
	return 'Hello world!'
