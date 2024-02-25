import random
import string
import traceback

from flask import Flask, request, abort, redirect
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from os import environ
from dotenv import load_dotenv

load_dotenv()
line_bot_api = LineBotApi(environ.get("LINE_BOT_API_TOKEN"))
handler = WebhookHandler(environ.get("LINE_BOT_CHANNEL_SECRET"))

app = Flask(__name__)

url_mapping = {}


@app.route('/hello', methods=['GET'])
def hello_world():
    return "Welcome to the service!"


def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for i in range(6))
    return short_url


@app.route('/<short_url>')
def redirect_to_long_url(short_url):
    if short_url in url_mapping:
        long_url = url_mapping[short_url]
        return redirect(long_url, code=302)
    else:
        return "URL not found", 404


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    if user_message.startswith("Shorten:"):
        long_url = user_message.split(":", 1)[1].strip()
        short_url = generate_short_url()
        url_mapping[short_url] = long_url
        reply_message = f"Shortened URL: {request.host_url}{short_url}"
    else:
        reply_message = "Invalid command. Please start your message with 'Shorten:' followed by the URL you want to " \
                        "shorten."

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except Exception as e:
        traceback.print_exc()
        print(e)
        abort(400)

    return "OK"


if __name__ == '__main__':
    app.run(port=environ.get("PORT", default=5000), debug=True)

