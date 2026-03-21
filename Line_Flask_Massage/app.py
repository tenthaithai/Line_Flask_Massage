from flask import Flask, request
import requests
import random
import os
import re
from groq import Groq
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# ===============================================================
# หมวดหมู่อาหาร (Category Constants)
# ===============================================================
CATEGORY_RICE       = "ข้าวจานเดียว"   # ข้าว/ก๋วยเตี๋ยว
CATEGORY_STIRFRY    = "ผัด"             # ผัด/炒
CATEGORY_SOUP       = "ต้ม/แกง"         # ซุป/แกง
CATEGORY_SALAD      = "ยำ/สลัด"         # ยำ/สลัด
CATEGORY_SEAFOOD    = "อาหารทะเล"       # อาหารทะเลเน้น
CATEGORY_GENERAL    = "ทั่วไป"          # ไม่ระบุชัดเจน

# ===============================================================
# เมนูอาหาร พร้อม category
# ===============================================================
food_menu = [
    {
        "name": "ข้าวมันไก่",
        "category": CATEGORY_RICE,
        "tags": ["มัน", "นุ่ม", "ข้าว", "ไก่", "ไม่เผ็ด"],
        "promotion": "ข้าวมันไก่ต้มนุ่ม หอมข้าวมันหอม",
        "image": "https://static.thairath.co.th/media/dFQROr7oWzulq5Fa6rpOetuLxWtDW4pGVxTIT2bhWuo8KUmcxGVIisEysxd9YsSVQ0b.webp",
        "price": "55",
    },
    {
        "name": "ผัดกะเพราหมูสับ",
        "category": CATEGORY_STIRFRY,
        "tags": ["เผ็ด", "ผัด", "หมู", "กะเพรา", "ข้าว"],
        "promotion": "ผัดกะเพราหมูสับกรอบ เผ็ดแซ่บ ใส่ไข่ดาว",
        "image": "https://cdn-ildplgb.nitrocdn.com/IsDIEVbKqjLKLwSjgUBetWWfJLAUdaLp/assets/images/optimized/rev-95ef742/www.thammculture.com/wp-content/uploads/2024/01/Untitled-612.jpg",
        "price": "60",
    },
    {
        "name": "ส้มตำไทย",
        "category": CATEGORY_SALAD,
        "tags": ["เผ็ด", "เปรี้ยว", "หวาน", "ยำ", "มะละกอ", "เส้น"],
        "promotion": "ส้มตำไทยสูตรต้นตำรับ เปรี้ยวหวานเผ็ด",
        "image": "https://cdn.hellokhunmor.com/wp-content/uploads/2019/10/107.-Thai-papaya-salad.jpg?w=750&q=100",
        "price": "50",
    },
    {
        "name": "ต้มยำกุ้ง",
        "category": CATEGORY_SOUP,
        "tags": ["เผ็ด", "เปรี้ยว", "กุ้ง", "ต้มยำ", "ซุป", "อาหารทะเล"],
        "promotion": "ต้มยำกุ้งน้ำข้นรสเข้มข้น กุ้งสดตัวใหญ่",
        "image": "https://www.creativeecon.asia/wp-content/uploads/2024/12/unnamed-1-696x389.jpg",
        "price": "120",
    },
    {
        "name": "ข้าวผัดปู",
        "category": CATEGORY_RICE,
        "tags": ["ผัด", "ปู", "ข้าว", "อาหารทะเล", "ไข่"],
        "promotion": "ข้าวผัดปูเนื้อปูแน่น หอมกลิ่นไข่",
        "image": "https://cdn.prod.website-files.com/629732c7c0e1401011449adc/6350f5166cfda1f319196a94_CrabFriedRice%402x-p-1600.webp",
        "price": "100",
    },
    # ── เพิ่มตัวอย่างหมวด seafood ──
    {
        "name": "ปลากะพงทอดน้ำปลา",
        "category": CATEGORY_SEAFOOD,
        "tags": ["ทอด", "ปลา", "อาหารทะเล", "กรอบ", "น้ำปลา"],
        "promotion": "ปลากะพงสดทอดกรอบ ราดน้ำปลาหอม",
        "image": "https://img.kapook.com/u/2019/surasin/cook2/seabass1.jpg",
        "price": "220",
    },
]

# สร้าง index จาก category → รายการเมนู
def build_category_index(menu: list) -> dict:
    index = {}
    for item in menu:
        cat = item["category"]
        index.setdefault(cat, []).append(item)
    return index

category_index = build_category_index(food_menu)

# ===============================================================
# System Instruction — สั่งให้ AI ระบุ category ท้ายข้อความ
# ===============================================================
CATEGORY_LIST_STR = ", ".join([
    CATEGORY_RICE, CATEGORY_STIRFRY, CATEGORY_SOUP,
    CATEGORY_SALAD, CATEGORY_SEAFOOD, CATEGORY_GENERAL
])

SYSTEM_INSTRUCTION = f"""
You are Food Master, your role is:
1. Check if User's message is about food or not.
2. If NOT food: reply exactly "ขออภัยครับ กระผมทราบแค่เรื่องอาหาร" and STOP.
3. If YES food:
   a. Analyze taste and ingredients from the message.
   b. Recommend at least 3 suitable Thai menus with brief explanation.
   c. At the very end of your reply, append a category tag on its own line:
      [CATEGORY:<category_name>]
      Choose ONE category from: {CATEGORY_LIST_STR}
      - ข้าวจานเดียว  → ข้าว, ก๋วยเตี๋ยว, ข้าวผัด
      - ผัด           → ผัดกะเพรา, ผัดซีอิ้ว, ผัดไทย
      - ต้ม/แกง       → ต้มยำ, แกงเขียวหวาน, ต้มข่า
      - ยำ/สลัด       → ส้มตำ, ยำวุ้นเส้น, ยำทะเล
      - อาหารทะเล     → ปลา, กุ้ง, ปู, หอย (ไม่ใช่ซุป)
      - ทั่วไป        → ไม่เข้าหมวดใดชัดเจน
4. Always answer in Thai language.
"""

# ===============================================================
# Helper: parse category tag จาก AI response
# ===============================================================
def parse_category(ai_reply: str) -> tuple[str, str]:
    """
    คืนค่า (clean_reply, category)
    - clean_reply : ข้อความที่ตัด [CATEGORY:...] ออกแล้ว
    - category    : ชื่อหมวดหมู่, default = CATEGORY_GENERAL
    """
    pattern = r"\[CATEGORY:(.+?)\]"
    match = re.search(pattern, ai_reply)
    category = match.group(1).strip() if match else CATEGORY_GENERAL
    clean_reply = re.sub(pattern, "", ai_reply).strip()
    return clean_reply, category


def get_food_by_category(category: str):
    """
    ดึงเมนูตาม category
    Fallback: ถ้าไม่มีเมนูในหมวดนั้น → สุ่มจากทั้งหมด
    """
    pool = category_index.get(category, [])
    if not pool:
        pool = food_menu          # fallback
    return random.choice(pool)


# ===============================================================
# Flex Message & LINE Reply (เหมือนเดิม)
# ===============================================================
CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")

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
                    {"type": "text", "text": food_item["name"], "size": "xl", "weight": "bold"},
                    {"type": "text", "text": food_item["promotion"], "size": "sm", "wrap": True},
                    {"type": "separator", "margin": "md"},
                    {
                        "type": "box",
                        "layout": "baseline",
                        "margin": "md",
                        "contents": [
                            {"type": "text", "text": "ราคา", "size": "sm", "flex": 1},
                            {"type": "text", "text": f"฿{food_item['price']}", "size": "lg",
                             "weight": "bold", "color": "#E53E3E", "flex": 2},
                        ],
                    },
                    # ── badge หมวดหมู่ ──
                    {
                        "type": "box",
                        "layout": "baseline",
                        "margin": "sm",
                        "contents": [
                            {"type": "text", "text": "หมวด", "size": "xs", "color": "#888888", "flex": 1},
                            {"type": "text", "text": food_item["category"], "size": "xs",
                             "color": "#F6A623", "flex": 2},
                        ],
                    },
                ],
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button", "style": "primary", "color": "#F6A623",
                        "action": {"type": "message", "label": "สั่งเลย!",
                                   "text": f"ขอสั่ง{food_item['name']}"},
                        "height": "sm",
                    },
                    {
                        "type": "button", "style": "secondary",
                        "action": {"type": "message", "label": "เมนูอื่น", "text": "กินอะไรดี"},
                        "height": "sm", "margin": "sm",
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
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=data)


# ===============================================================
# Webhook
# ===============================================================
@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.get_json()
    for event in payload.get("events", []):
        if event["type"] != "message" or event["message"]["type"] != "text":
            continue

        user_text = event["message"]["text"].strip()
        reply_token = event["replyToken"]

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "user",   "content": user_text},
                ],
                model="llama-3.3-70b-versatile",
            )
            raw_reply = chat_completion.choices[0].message.content.strip()

            # ── ไม่ใช่เรื่องอาหาร ──
            if "ขออภัยครับ กระผมทราบแค่เรื่องอาหาร" in raw_reply:
                send_reply(reply_token, [{"type": "text", "text": raw_reply}])
                continue

            # ── Parse category → เลือกเมนูตรงหมวด ──
            ai_reply, category = parse_category(raw_reply)
            selected_food = get_food_by_category(category)

            send_reply(reply_token, [
                {"type": "text", "text": ai_reply},
                create_flex_message(selected_food),
            ])

        except Exception as e:
            print(f"Error: {e}")
            send_reply(reply_token, [{"type": "text", "text": "ขออภัยครับ ระบบประมวลผลขัดข้อง"}])

    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)