from flask import Flask, request
import requests
import os

app = Flask(__name__)

# 從 Render 的環境變數讀取 LINE Access Token
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
# OpenRouter API 金鑰
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# LINE 回覆用的 Header
LINE_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
}

# OpenRouter 請求用的 Header
OPENROUTER_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENROUTER_API_KEY}"
}

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.get_json()
    event = body["events"][0]
    user_text = event["message"]["text"]
    reply_token = event["replyToken"]

    # 發送給 OpenRouter 的 Prompt 設定
    payload = {
        "model": "google/gemini-flash-1.5",
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是一位溫柔正向、善於安慰人的心靈導師。\n"
                    "請根據使用者的文字，生成一段約 80～150 字的心靈雞湯內容。\n"
                    "內容要鼓勵人、充滿希望、正面積極，避免具體知識與指令教學。\n"
                    "請使用溫暖的語氣，像朋友一樣說話，可以適當加入 Emoji（如 🌸🌈☀️💖）。"
                )
            },
            {
                "role": "user",
                "content": user_text
            }
        ]
    }

    # 向 OpenRouter 發出請求
    res = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=OPENROUTER_HEADERS,
        json=payload
    )

    # 取得 AI 回應文字
    result = res.json()
    ai_reply = result["choices"][0]["message"]["content"]

    # 傳送給 LINE 使用者
    reply_body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": ai_reply}]
    }

    requests.post(
        "https://api.line.me/v2/bot/message/reply",
        headers=LINE_HEADERS,
        json=reply_body
    )

    return "OK"

if __name__ == "__main__":
    app.run()
