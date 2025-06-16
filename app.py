from flask import Flask, request
import requests
import os

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

LINE_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
}

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

    # ✅ 無關主題關鍵字過濾（避免寫程式、技術、閒聊等）
    banned_keywords = [
        "寫程式", "教我", "語法", "API", "GPT", "Python", "JavaScript", "怎麼做", 
        "是什麼", "解釋", "知識", "ChatGPT", "資料庫", "openai", "翻譯", "代碼",
        "定義", "遊戲", "猜拳", "笑話", "故事", "詩", "數學", "單字", "爬蟲"
    ]

    if any(keyword.lower() in user_text.lower() for keyword in banned_keywords):
        ai_reply = "這裡是溫暖的心靈角落 😊 我專門陪你聊聊情緒與人生唷～有什麼煩惱或感受想說說嗎？🌿"
    else:
        payload = {
            "model": "google/gemini-flash-1.5",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是一位溫暖正向的心靈導師，只回答與人生、情緒、心理支持有關的問題。\n"
                        "不允許回答任何與技術、程式、遊戲、閒聊、知識查詢、邏輯推理或科學問題。\n"
                        "請使用鼓舞人心、同理理解的語氣來回應。\n"
                        "每次回應請在 80～150 字內，可加入 Emoji（🌈💖🌿💪），像朋友一樣關心對方。"
                    )
                },
                {"role": "user", "content": user_text}
            ]
        }

        res = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=OPENROUTER_HEADERS,
            json=payload
        )

        try:
            result = res.json()
            ai_reply = result["choices"][0]["message"]["content"]
        except:
            ai_reply = "⚠️ 抱歉，AI 回覆時發生問題，請稍後再試～我會一直在這裡等你 🌟"

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
