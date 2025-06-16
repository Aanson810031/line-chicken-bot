from flask import Flask, request
import requests
import os

app = Flask(__name__)

# 讀取金鑰
LINE_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

LINE_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {LINE_TOKEN}"
}

@app.route("/")
def home():
    return "✅ LINE BOT with Gemini Flash is running."

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("📩 收到 LINE 資料：", data)

    if "events" not in data:
        return "No event"

    event = data["events"][0]
    if event["type"] != "message" or event["message"]["type"] != "text":
        return "Not text"

    user_text = event["message"]["text"]
    reply_token = event["replyToken"]

    # 一律交給 Gemini Flash 回應
    try:
        ai_response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-pro",
                "messages": [
                    {"role": "system", "content": "你是一個溫暖而積極的 LINE AI 助理"},
                    {"role": "user", "content": user_text}
                ]
            }
        )

        reply = ai_response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("❌ Gemini API 錯誤：", e)
        reply = "⚠️ 抱歉，AI 回覆發生錯誤，請稍後再試。"

    # 發送回 LINE 使用者
    body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": reply}]
    }

    r = requests.post("https://api.line.me/v2/bot/message/reply",
                      headers=LINE_HEADERS, json=body)
    print("📝 發送結果：", r.status_code, r.text)
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
