from flask import Flask, request
import requests
import random
import os

app = Flask(__name__)

# LINE Channel Settings
CHANNEL_ACCESS_TOKEN = os.environ.get(
    "LINE_CHANNEL_ACCESS_TOKEN",
    "edF0a5LKdkP7jHEXvKXIpgohbfNjk8djOYkIYLxPef+jhnVOpZafC7xhds/M+iQIadpOYZbla8EscJ7FYxzQ6RwEe0yCbTQrO/A3qo08b1cG8pkTxcLjFoGI2aiiXBIO9cfj3RVHZumjKypjhlHYHgdB04t89/1O/w1cDnyilFU=",
)
CHANNEL_SECRET = os.environ.get(
    "LINE_CHANNEL_SECRET", "142b833b66b98f24e01e7d1ca0b470f3"
)

# Food Menu List
food_menu = [
    {
        "name": "ข้าวมันไก่",
        "promotion": "ข้าวมันไก่ต้มนุ่ม หอมข้าวมันหอม พร้อมน้ำจิ้มสูตรเด็ด",
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
        "promotion": "ส้มตำไทยสูตรต้นตำรับ เปรี้ยวหวานเผ็ด ถูกปาก",
        "image": "https://cdn.hellokhunmor.com/wp-content/uploads/2019/10/107.-Thai-papaya-salad.jpg?w=750&q=100",
        "price": "50",
    },
    {
        "name": "ต้มยำกุ้ง",
        "promotion": "ต้มยำกุ้งน้ำข้นรสเข้มข้น กุ้งสดตัวใหญ่ อร่อยมาก",
        "image": "https://www.creativeecon.asia/wp-content/uploads/2024/12/unnamed-1-696x389.jpg",
        "price": "120",
    },
    {
        "name": "ข้าวผัดปู",
        "promotion": "ข้าวผัดปูเนื้อปูแน่น หอมกลิ่นไข่ รสชาติกลมกล่อม",
        "image": "https://cdn.prod.website-files.com/629732c7c0e1401011449adc/6350f5166cfda1f319196a94_CrabFriedRice%402x-p-1600.webp",
        "price": "100",
    },
]

# Supported Keywords
food_keywords = []


# Create Flex Message
def create_flex_message(food_item):
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
                        "color": "#222222",
                    },
                    {
                        "type": "text",
                        "text": food_item["promotion"],
                        "size": "sm",
                        "color": "#666666",
                        "wrap": True,
                    },
                    {"type": "separator", "margin": "md"},
                    {
                        "type": "box",
                        "layout": "baseline",
                        "margin": "md",
                        "contents": [
                            {
                                "type": "text",
                                "text": "ราคา",
                                "size": "sm",
                                "color": "#999999",
                                "flex": 1,
                            },
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


# Send Reply Message to User
def send_reply(reply_token, messages):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }
    data = {
        "replyToken": reply_token,
        "messages": messages if isinstance(messages, list) else [messages],
    }
    response = requests.post(
        "https://api.line.me/v2/bot/message/reply", headers=headers, json=data
    )
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)


# Receive Webhook from LINE
@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.get_json()
    print("📥 Received:", payload)

    for event in payload.get("events", []):
        # Support only text message type
        if event["type"] != "message" or event["message"]["type"] != "text":
            continue

        received_text = event["message"]["text"].strip()
        reply_token = event["replyToken"]

        if received_text in food_keywords:
            # Randomize menu and reply with Flex Message
            selected_food = random.choice(food_menu)
            send_reply(reply_token, [create_flex_message(selected_food)])
        else:
            # Other keywords: Reply not understand
            send_reply(reply_token, [{"type": "text", "text": "ฉันไม่เข้าใจ"}])

    return "OK", 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)
