from flask import Flask, request
import requests
import os

app = Flask(__name__)

# 讀取環境變數
LINE_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

LINE_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {LINE_TOKEN}"
}

@app.route("/")
def home():
    return "✅ LINE BOT with Gemini is running."

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

    # 判斷是否使用 AI 回覆（#AI 開頭才觸發）
    if user_text.startswith("#AI "):
        prompt = user_text[4:]

        # 呼叫 OpenRouter API - Gemini 2.0 Flash
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-pro-vision",  # 可用 "google/gemini-pro" 或其他
                "messages": [
                    {"role": "system", "content": "你是一個正面溫柔的 AI 助理"},
                    {"role": "user", "content": prompt}
                ]
            }
        )

        try:
            reply = response.json()["choices"][0]["message"]["content"]
        except:
            reply = "⚠️ 抱歉，AI 回覆失敗，請稍後再試。"
    else:
        # 預設回應
        if "難過" in user_text or "疲累" in user_text or "低落" in user_text:
            reply = "別難過，一切都會過去的。🌈"
        else:
            reply = "今天也要記得微笑！🙂"

    # 發送回覆訊息
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
