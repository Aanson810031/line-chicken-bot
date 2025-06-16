from flask import Flask, request
import requests
import os

app = Flask(__name__)

# 從環境變數取得金鑰
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# LINE 回應所需的 Header
LINE_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
}

# OpenRouter API Header
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

    # 🚫 不允許的關鍵詞（非心靈雞湯主題）
    banned_keywords = [
        "寫程式", "python", "api", "教我", "語法", "怎麼做", "chatgpt", "模型", "定義",
        "翻譯", "openai", "爬蟲", "資料庫", "數學", "笑話", "故事", "遊戲", "代碼", "語言"
    ]

    # ✅ 若出現禁止關鍵詞，直接給固定回覆
    if any(word in user_text.lower() for word in banned_keywords):
        ai_reply = "這裡是溫暖的心靈角落 😊 我只專注陪你聊聊情緒與人生唷～有什麼煩惱或感受想說說嗎？🌿"
    else:
        # ✅ 呼叫 Gemini Flash 生成心靈雞湯
        payload = {
            "model": "google/gemini-flash-1.5",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是一位溫柔的心靈導師，只回答與情緒、人生、心靈支持有關的問題。\n"
                        "嚴禁回答技術、寫程式、遊戲、查資料、搞笑、科普、百科、閒聊類問題。\n"
                        "請用理解、鼓勵、陪伴的方式來回應，字數介於 80～150 字，並搭配合適 Emoji 🌈💖🌿💪。\n"
                        "如果對方問題不太相關，也請婉轉引導他回到情緒與生活話題。"
                    )
                },
                {"role": "user", "content": user_text}
            ]
        }

        try:
            res = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=OPENROUTER_HEADERS,
                json=payload
            )
            result = res.json()
            ai_reply = result["choices"][0]["message"]["content"]
        except Exception as e:
            print("OpenRouter error:", e)
            ai_reply = "⚠️ 抱歉，AI 回覆時發生問題，請稍後再試～我會一直在這裡等你 🌟"

    # 回傳訊息給 LINE
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

# ✅ 正確綁定埠口以支援 Render 部署
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
