from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ✅ 改為從環境變數讀取 Token（Render 已設定）
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")

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

    # 心靈雞湯回應
    if "難過" in text or "疲累" in text or "低落" in text:
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

if __name__ == "__main__":
    app.run()
