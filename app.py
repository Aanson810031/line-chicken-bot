from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ✅ 從環境變數取得 Channel Access Token
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📩 收到 LINE 資料：", data)  # ✅ 這行是 debug log

    # 防呆：無事件就跳出
    if "events" not in data or len(data["events"]) == 0:
        return "No events"

    event = data["events"][0]

    # 防呆：不是文字訊息就跳出
    if event["type"] != "message" or event["message"]["type"] != "text":
        return "Not text"

    text = event["message"]["text"]
    reply_token = event["replyToken"]

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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

