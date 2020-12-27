import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_text_message
from crawling import *

load_dotenv()

machine = TocMachine(
    states=["lobby", "champion_data", "player_data"],
    transitions=[
        {
            "trigger": "advance",
            "source": "lobby",
            "dest": "champion_data",
            "conditions": "is_going_to_champion_data",
        },
        {
            "trigger": "advance",
            "source": "lobby",
            "dest": "player_data",
            "conditions": "is_going_to_player_data",
        },
        {"trigger": "go_back", "source": ["champion_data", "player_data"], "dest": "lobby"},
    ],
    initial="lobby",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

champion_name = ''

'''
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"
'''

@app.route("/webhook", methods=["POST"])
def webhook_handler():
    global champion_name
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = False
        if machine.state == 'lobby':
            response = machine.advance(event)
        if response == False:
            if machine.state == 'champion_data':
                if event.message.text.upper() == 'B':
                    if champion_name == "":
                        machine.go_back()
                        send_text_message(event.reply_token, "查詢英雄資訊請輸入1\n查詢玩家資訊請輸入2\n輸入B可於任何步驟返回上一步")
                    else:
                        champion_name = ""
                        send_text_message(event.reply_token, "請輸入欲查詢的英雄名稱")
                else:
                    if champion_name == "":
                        result = is_champion(event.message.text)
                        if result[0]:
                            champion_name = result[1]
                            send_text_message(event.reply_token, champion_statistics(champion_name) + "如果想查看技能資訊請輸入P、Q、W、E、R")
                        else:
                            send_text_message(event.reply_token, "查無此英雄，請重新輸入")
                    else:
                        result = champion_ability(champion_name, event.message.text)
                        if result != "":
                            send_text_message(event.reply_token, result)
            elif machine.state =='player_data':
                if event.message.text.upper() == 'B':
                    machine.go_back()
                    send_text_message(event.reply_token, "查詢英雄資訊請輸入1\n查詢玩家資訊請輸入2\n輸入B可於任何步驟返回上一步")
                else:
                    result = player_search(event.message.text)
                    if result == 'Not Found':
                        send_text_message(event.reply_token, "查無此玩家或是伺服忙線中")
                    else:
                        send_text_message(event.reply_token, result)
            else:
                send_text_message(event.reply_token, "查詢英雄資訊請輸入1\n查詢玩家資訊請輸入2\n輸入B可於任何步驟返回上一步")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
