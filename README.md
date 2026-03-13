# Line_Flask_Massage
================================================================
  คู่มือการติดตั้งและรัน LINE Chatbot (Flask) บนเครื่องใหม่
================================================================

---------------------------------
1. สิ่งที่ต้องติดตั้งก่อน
---------------------------------

	1.1 Python (แนะนำเวอร์ชัน 3.8 ขึ้นไป)
    	ดาวน์โหลด: https://www.python.org/downloads/
    	- ติ๊ก "Add Python to PATH" ตอนติดตั้งด้วย

	1.2 ngrok
    	ดาวน์โหลด: https://ngrok.com/download
    	- สมัครบัญชีฟรีที่ https://dashboard.ngrok.com/signup
    	- หลังสมัครแล้ว copy Authtoken จาก dashboard มาใส่


---------------------------------
2. ติดตั้ง Library ที่จำเป็น
---------------------------------

เปิด Command Prompt หรือ Terminal แล้วพิมพ์:

    pip install flask requests

(ถ้ามี requirements.txt ให้รัน: pip install -r requirements.txt)


---------------------------------
3. วางไฟล์โปรเจกต์
---------------------------------

โครงสร้างโฟลเดอร์ที่ต้องมี:

    Line_Flask_Massage/
    └── app.py


---------------------------------
4. ตั้งค่า Token และ Secret
---------------------------------

เปิดไฟล์ app.py แล้วแก้ค่าตรงนี้:

    CHANNEL_ACCESS_TOKEN = "ใส่ token ของคุณที่นี่"
    CHANNEL_SECRET      = "ใส่ secret ของคุณที่นี่"

หรือตั้งเป็น Environment Variable แทน (แนะนำ):

    Windows (CMD):
        set LINE_CHANNEL_ACCESS_TOKEN=xxxxxxx
        set LINE_CHANNEL_SECRET=xxxxxxx

    Mac/Linux:
        export LINE_CHANNEL_ACCESS_TOKEN=xxxxxxx
        export LINE_CHANNEL_SECRET=xxxxxxx

หา Token และ Secret ได้ที่:
    https://developers.line.biz → เลือก Channel → Messaging API


---------------------------------
5. รัน Flask
---------------------------------

เปิด Terminal แล้ว cd ไปที่โฟลเดอร์โปรเจกต์:

    cd ("YOUR_PATH")

รัน app:

    python app.py

ถ้าสำเร็จจะเห็น:
    * Running on http://127.0.0.1:5000


---------------------------------
6. รัน ngrok (เปิด Terminal ใหม่อีกอัน)
---------------------------------

ครั้งแรก ต้อง login ngrok ก่อน (ทำครั้งเดียว):

    ngrok config add-authtoken YOUR_AUTHTOKEN

จากนั้นรัน:

    ngrok http 5000

จะได้ URL ประมาณนี้:
    https://xxxx-xxxx-xxxx.ngrok-free.dev

** URL นี้จะเปลี่ยนทุกครั้งที่รัน ngrok ใหม่ (แผน Free)


---------------------------------
7. ตั้งค่า Webhook ใน LINE Developers Console
---------------------------------

	7.1 ไปที่ https://developers.line.biz
	7.2 เลือก Channel ของคุณ → Messaging API
	7.3 หัวข้อ "Webhook settings":
   	- Webhook URL: ใส่ URL จาก ngrok + /webhook
     		ตัวอย่าง: https://xxxx-xxxx-xxxx.ngrok-free.dev/webhook
   	- กด "Update" แล้วกด "Verify"
   	- เปิด "Use webhook" ให้เป็น ON

	7.4 หัวข้อ "LINE Official Account features":
   	- Auto-reply messages → ปิด (Disabled)
   	- Greeting messages  → ปิด (Disabled) [ถ้าไม่ต้องการ]


---------------------------------
8. ทดสอบ
---------------------------------

ส่งข้อความใน LINE:
    - "หิวข้าว"
    - "กินอะไรดี"
    - "แนะนำร้านอาหาร"

Bot จะตอบกลับด้วย Flex Message แนะนำเมนูอาหาร


---------------------------------
9. หมายเหตุสำคัญ
---------------------------------

- ต้องเปิด Flask และ ngrok ทิ้งไว้ตลอดเวลาที่ใช้งาน Bot
- ngrok แผน Free URL จะเปลี่ยนทุกครั้งที่รีสตาร์ท
  → ต้องอัปเดต Webhook URL ใน LINE Developers Console ใหม่ทุกครั้ง
- ห้ามแชร์ CHANNEL_ACCESS_TOKEN และ CHANNEL_SECRET ให้คนอื่น
- ถ้าต้องการ URL คงที่ ให้อัปเกรด ngrok หรือ deploy ขึ้น cloud
  เช่น Render, Railway, หรือ Google Cloud Run (ฟรี)


================================================================
  หากมีปัญหา ให้เช็ค:
  1. Flask รันอยู่ไหม? (ดูใน terminal แรก)
  2. ngrok รันอยู่ไหม? (ดูใน terminal ที่สอง)
  3. Webhook URL ใน LINE ตรงกับ ngrok URL ปัจจุบันไหม?
  4. "Use webhook" เปิดอยู่ไหม?
================================================================
