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

    # ✅ 加強限制：只允許心靈雞湯，拒答不相關問題
    payload = {
        "model": "google/gemini-flash-1.5",
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是一位溫暖、正向的心靈導師，只回答關於情緒、人生、心靈成長的問題。\n"
                    "不允許回應任何與寫程式、知識查詢、指令操作、遊戲互動或閒聊等不相關主題。\n"
                    "若使用者提出與主題無關的問題（如幫我寫程式、查資料、解釋概念等），請禮貌婉拒，並鼓勵對方說出內心感受。\n"
                    "回應語氣要像一位理解人的朋友，文字要正面勵志、溫柔鼓舞，並盡量在 80～150 字內完成。\n"
                    "可以使用 Emoji（如 ☀️🌸🌈💖）來傳達溫度。"
                )
            },
            {
                "role": "user",
                "content": user_text
            }
        ]
    }

    res = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=OPENROUTER_HEADERS,
        json=payload
    )

    result = res.json()
    ai_reply = result["choices"][0]["message"]["content"]

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
