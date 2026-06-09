import os
from flask import Flask, request
import google.generativeai as genai
import requests

app = Flask(__name__)

# --- ส่วนที่คุณต้องเติมเอง ---
GEMINI_API_KEY = "AQ.Ab8RN6K6oiBrcMYy4KDwDyMBITzZdlu9RV9ze9KRsS91WE2Dtg"
PAGE_ACCESS_TOKEN = "EAAcUb1R7QGgBRvP1HlDJyQyxBGdm152HZAcySAH0I3slpkK9mwZBBLZALtNEkFSn6dzC7lc1zXVkjognEOZC3TtZAtgNk538RlA9BYEhPkFTM1dFTwAZCSHgiUhgnwoFPZARsbUYk4m3AMzhTUL6GdK3S2138ucZAtXWbcMUV7XqWLxYKsKlr0ytL7xVbZAtTLxFZAHg0s"
VERIFY_TOKEN = "Rattanathibet!01" # ใช้ตอนเชื่อม Facebook ครั้งแรก

# ข้อมูลธุรกิจของคุณ (Knowledge Base)
KNOWLEDGE_BASE = """
คุณคือแอดมินตอบแชทของ ศูนย์บริการสาธารณสุขที่ 1 รัตนาธิเบศร์
ข้อมูลบริการ:
- เวลาทำการ: จันทร์-ศุกร์ 08.00 - 16.00 น.
- บริการหลัก: ตรวจรักษาโรคทั่วไป, ฉีดวัคซีน, ตรวจสุขภาพ
- เบอร์โทรศัพท์: 02-xxx-xxxx
(คุณสามารถเพิ่มข้อมูลอื่นๆ ลงไปได้แบบไม่จำกัดตรงนี้)
"""

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@app.route("/", methods=['GET'])
def verify():
    # สำหรับให้ Facebook ตรวจสอบ Webhook
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Hello AI Bot"

@app.route("/", methods=['POST'])
def webhook():
    data = request.get_json()
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    user_text = messaging_event["message"]["text"]
                    
                    # ส่งไปถาม Gemini
                    prompt = f"{KNOWLEDGE_BASE}\n\nลูกค้าถามว่า: {user_text}\nตอบอย่างสุภาพและเป็นกันเอง:"
                    response = model.generate_content(prompt)
                    ai_response = response.text
                    
                    # ส่งคำตอบกลับไปที่ Facebook
                    send_message(sender_id, ai_response)
    return "ok", 200

def send_message(recipient_id, message_text):
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post("https://graph.facebook.com/v19.0/me/messages", params=params, headers=headers, json=data )

if __name__ == "__main__":
    app.run(port=5000)
