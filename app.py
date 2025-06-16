from flask import Flask, request
import requests
import os

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = "你的 Access Token"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    event = data["events"][0]
    text = event["message"]["text"]
    reply_token = event["replyToken"]

    if "難過" in text:
        reply = "別難過，一切都會過去的。🌈"
    else:
        reply = "今天也要記得微笑！🙂"

    body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": reply}]
    }

    requests.post("https://api.line.me/v2/bot/message/reply",
                  headers=HEADERS, json=body)

    return "OK"

# ✅ 這段一定要有！
if __name__ == "__main__":
    app.run()
