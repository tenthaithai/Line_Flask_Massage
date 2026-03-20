from flask import Flask, request
import requests
import random
import os
from groq import Groq  # เปลี่ยน Library เป็น groq

app = Flask(__name__)

# --- Configuration API Keys (Groq Cloud) ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")
client = Groq(api_key=GROQ_API_KEY)

# กำหนด System Instruction สำหรับ Groq
SYSTEM_INSTRUCTION = """
    You are Food Master, your role is:
    1. Check User Conversation (That Conver. is Food Or Not)
    2. If Not Food Say "ขออภัยครับ กระผมทราบแค่เรื่องอาหาร"
    3. If Yes Then Analysis Taste and Component And Recommend To User (Min. 3 Menu)
    4. If User Not Corrent Conversation Check Conversation Confident Before Analysis
    5. Answer in Thai language.
"""

# LINE Channel Settings
CHANNEL_ACCESS_TOKEN = os.environ.get(
    "LINE_CHANNEL_ACCESS_TOKEN",
    "edF0a5LKdkP7jHEXvKXIpgohbfNjk8djOYkIYLxPef+jhnVOpZafC7xhds/M+iQIadpOYZbla8EscJ7FYxzQ6RwEe0yCbTQrO/A3qo08b1cG8pkTxcLjFoGI2aiiXBIO9cfj3RVHZumjKypjhlHYHgdB04t89/1O/w1cDnyilFU=",
)

# Food Menu List (ยังคงเดิม)
food_menu = [
    {
        "name": "ข้าวมันไก่",
        "promotion": "ข้าวมันไก่ต้มนุ่ม หอมข้าวมันหอม",
        "image": "https://static.thairath.co.th/media/dFQROr7oWzulq5Fa6rpOetuLxWtDW4pGVxTIT2bhWuo8KUmcxGVIisEysxd9YsSVQ0b.webp",
        "price": "55",
    },
    {
        "name": "ผัดกะเพราหมูสับ",
        "promotion": "ผัดกะเพราหมูสับกรอบ เผ็ดแซ่บ ใส่ไข่ดาว",
        "image": "https://cdn-ildplgb.nitrocdn.com/IsDIEVbKqjLKLwSjgUBetWWfJLAUdaLp/assets/images/optimized/rev-95ef742/www.thammculture.com/wp-content/uploads/2024/01/Untitled-612.jpg",
        "price": "60",
    },
    {
        "name": "ส้มตำไทย",
        "promotion": "ส้มตำไทยสูตรต้นตำรับ เปรี้ยวหวานเผ็ด",
        "image": "https://cdn.hellokhunmor.com/wp-content/uploads/2019/10/107.-Thai-papaya-salad.jpg?w=750&q=100",
        "price": "50",
    },
    {
        "name": "ต้มยำกุ้ง",
        "promotion": "ต้มยำกุ้งน้ำข้นรสเข้มข้น กุ้งสดตัวใหญ่",
        "image": "https://www.creativeecon.asia/wp-content/uploads/2024/12/unnamed-1-696x389.jpg",
        "price": "120",
    },
    {
        "name": "ข้าวผัดปู",
        "promotion": "ข้าวผัดปูเนื้อปูแน่น หอมกลิ่นไข่",
        "image": "https://cdn.prod.website-files.com/629732c7c0e1401011449adc/6350f5166cfda1f319196a94_CrabFriedRice%402x-p-1600.webp",
        "price": "100",
    },
]


def create_flex_message(food_item):
    # (โค้ดส่วนนี้เหมือนเดิมทุุกประการ)
    return {
        "type": "flex",
        "altText": f"แนะนำเมนู: {food_item['name']}",
        "contents": {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": food_item["image"],
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "text",
                        "text": food_item["name"],
                        "size": "xl",
                        "weight": "bold",
                    },
                    {
                        "type": "text",
                        "text": food_item["promotion"],
                        "size": "sm",
                        "wrap": True,
                    },
                    {"type": "separator", "margin": "md"},
                    {
                        "type": "box",
                        "layout": "baseline",
                        "margin": "md",
                        "contents": [
                            {"type": "text", "text": "ราคา", "size": "sm", "flex": 1},
                            {
                                "type": "text",
                                "text": f"฿{food_item['price']}",
                                "size": "lg",
                                "weight": "bold",
                                "color": "#E53E3E",
                                "flex": 2,
                            },
                        ],
                    },
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": "#F6A623",
                        "action": {
                            "type": "message",
                            "label": "สั่งเลย!",
                            "text": f"ขอสั่ง{food_item['name']}",
                        },
                        "height": "sm",
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "action": {
                            "type": "message",
                            "label": "เมนูอื่น",
                            "text": "กินอะไรดี",
                        },
                        "height": "sm",
                        "margin": "sm",
                    },
                ],
            },
        },
    }


def send_reply(reply_token, messages):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }
    data = {
        "replyToken": reply_token,
        "messages": messages if isinstance(messages, list) else [messages],
    }
    requests.post(
        "https://api.line.me/v2/bot/message/reply", headers=headers, json=data
    )


@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.get_json()
    for event in payload.get("events", []):
        if event["type"] != "message" or event["message"]["type"] != "text":
            continue

        user_text = event["message"]["text"].strip()
        reply_token = event["replyToken"]

        try:
            # --- ส่วนที่เชื่อมต่อกับ Groq Cloud ---
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user", "content": user_text},
                ],
                model="llama-3.3-70b-versatile",  # หรือใช้ "llama3-8b-8192" ก็ได้ครับ
            )
            ai_reply = chat_completion.choices[0].message.content.strip()

            if "ขออภัยครับ กระผมทราบแค่เรื่องอาหาร" in ai_reply:
                send_reply(reply_token, [{"type": "text", "text": ai_reply}])
            else:
                selected_food = random.choice(food_menu)
                messages = [
                    {"type": "text", "text": ai_reply},
                    create_flex_message(selected_food),
                ]
                send_reply(reply_token, messages)

        except Exception as e:
            print(f"Error: {e}")
            send_reply(
                reply_token, [{"type": "text", "text": "ขออภัยครับ ระบบประมวลผลขัดข้อง"}]
            )

    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
