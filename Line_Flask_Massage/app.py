from flask import Flask, request
import requests
import random
import os

app = Flask(__name__)

# ตั้งค่า Token และ Secret ของ LINE
CHANNEL_ACCESS_TOKEN = os.environ.get(
    "LINE_CHANNEL_ACCESS_TOKEN",
    "edF0a5LKdkP7jHEXvKXIpgohbfNjk8djOYkIYLxPef+jhnVOpZafC7xhds/M+iQIadpOYZbla8EscJ7FYxzQ6RwEe0yCbTQrO/A3qo08b1cG8pkTxcLjFoGI2aiiXBIO9cfj3RVHZumjKypjhlHYHgdB04t89/1O/w1cDnyilFU=",
)
CHANNEL_SECRET = os.environ.get(
    "LINE_CHANNEL_SECRET", "142b833b66b98f24e01e7d1ca0b470f3"
)

# รายการเมนูอาหาร
รายการอาหาร = [
    {
        "ชื่อ": "ข้าวมันไก่",
        "โปรโมชัน": "ข้าวมันไก่ต้มนุ่ม หอมข้าวมันหอม พร้อมน้ำจิ้มสูตรเด็ด",
        "รูป": "https://static.thairath.co.th/media/dFQROr7oWzulq5Fa6rpOetuLxWtDW4pGVxTIT2bhWuo8KUmcxGVIisEysxd9YsSVQ0b.webp",
        "ราคา": "55",
    },
    {
        "ชื่อ": "ผัดกะเพราหมูสับ",
        "โปรโมชัน": "ผัดกะเพราหมูสับกรอบ เผ็ดแซ่บ ใส่ไข่ดาว",
        "รูป": "https://cdn-ildplgb.nitrocdn.com/IsDIEVbKqjLKLwSjgUBetWWfJLAUdaLp/assets/images/optimized/rev-95ef742/www.thammculture.com/wp-content/uploads/2024/01/Untitled-612.jpg",
        "ราคา": "60",
    },
    {
        "ชื่อ": "ส้มตำไทย",
        "โปรโมชัน": "ส้มตำไทยสูตรต้นตำรับ เปรี้ยวหวานเผ็ด ถูกปาก",
        "รูป": "https://cdn.hellokhunmor.com/wp-content/uploads/2019/10/107.-Thai-papaya-salad.jpg?w=750&q=100",
        "ราคา": "50",
    },
    {
        "ชื่อ": "ต้มยำกุ้ง",
        "โปรโมชัน": "ต้มยำกุ้งน้ำข้นรสเข้มข้น กุ้งสดตัวใหญ่ อร่อยมาก",
        "รูป": "https://www.creativeecon.asia/wp-content/uploads/2024/12/unnamed-1-696x389.jpg",
        "ราคา": "120",
    },
    {
        "ชื่อ": "ข้าวผัดปู",
        "โปรโมชัน": "ข้าวผัดปูเนื้อปูแน่น หอมกลิ่นไข่ รสชาติกลมกล่อม",
        "รูป": "https://cdn.prod.website-files.com/629732c7c0e1401011449adc/6350f5166cfda1f319196a94_CrabFriedRice%402x-p-1600.webp",
        "ราคา": "100",
    },
]

# คีย์เวิร์ดที่รองรับ
คีย์เวิร์ดอาหาร = ["แนะนำร้เมนูอาหาร", "กินอะไรดี", "หิวข้าว"]


# สร้าง Flex Message
def สร้างFlexMessage(อาหาร):
    return {
        "type": "flex",
        "altText": f"แนะนำเมนู: {อาหาร['ชื่อ']}",
        "contents": {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": อาหาร["รูป"],
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
                        "text": อาหาร["ชื่อ"],
                        "size": "xl",
                        "weight": "bold",
                        "color": "#222222",
                    },
                    {
                        "type": "text",
                        "text": อาหาร["โปรโมชัน"],
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
                                "text": f"฿{อาหาร['ราคา']}",
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
                            "text": f"ขอสั่ง{อาหาร['ชื่อ']}",
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


# ส่งข้อความกลับไปหาผู้ใช้
def ตอบกลับ(replyToken, ข้อความ):
    หัวข้อ = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    }
    ข้อมูล = {
        "replyToken": replyToken,
        "messages": ข้อความ if isinstance(ข้อความ, list) else [ข้อความ],
    }
    ผล = requests.post(
        "https://api.line.me/v2/bot/message/reply", headers=หัวข้อ, json=ข้อมูล
    )
    print("STATUS:", ผล.status_code)
    print("RESPONSE:", ผล.text)


# รับ Webhook จาก LINE
@app.route("/webhook", methods=["POST"])
def webhook():
    ข้อมูล = request.get_json()
    print("📥 ได้รับ:", ข้อมูล)

    for เหตุการณ์ in ข้อมูล.get("events", []):
        # รองรับเฉพาะข้อความประเภทข้อความ
        if เหตุการณ์["type"] != "message" or เหตุการณ์["message"]["type"] != "text":
            continue

        ข้อความที่รับ = เหตุการณ์["message"]["text"].strip()
        replyToken = เหตุการณ์["replyToken"]

        if ข้อความที่รับ in คีย์เวิร์ดอาหาร:
            # สุ่มเมนูแล้วตอบด้วย Flex Message
            อาหารที่เลือก = random.choice(รายการอาหาร)
            ตอบกลับ(replyToken, [สร้างFlexMessage(อาหารที่เลือก)])
        else:
            # คีย์เวิร์ดอื่นตอบว่าไม่เข้าใจ
            ตอบกลับ(replyToken, [{"type": "text", "text": "ฉันไม่เข้าใจ"}])

    return "OK", 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)

