from flask import request, abort, current_app
from . import linebot_bp
from app.models import ServiceJob, ServiceJobStatus
from datetime import date

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# สร้าง Handler ไว้ก่อน แต่จะไปตั้งค่า Channel Secret จริงๆ ใน app/__init__.py
# เพื่อป้องกันปัญหา Circular Import และใช้ค่า Config ล่าสุดเสมอ
handler = WebhookHandler("placeholder_secret")

@linebot_bp.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        # Handler จะมี Channel Secret ที่ถูกต้องแล้ว ณ จุดนี้
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        current_app.logger.error(f"Error handling webhook: {e}")
        abort(500)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text.strip().lower()
    
    with ApiClient(Configuration(access_token=current_app.config['LINE_CHANNEL_ACCESS_TOKEN'])) as api_client:
        line_bot_api = MessagingApi(api_client)
        reply_text = process_command(text)
        
        if reply_text:
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_text)]
                )
            )

def process_command(text):
    """ประมวลผลคำสั่งจากผู้ใช้และส่งข้อความตอบกลับ"""
    if text == 'งานวันนี้':
        # ในอนาคตจะเพิ่ม Logic การดึงข้อมูลจากฐานข้อมูล
        return "ฟังก์ชัน 'งานวันนี้' กำลังอยู่ในระหว่างการพัฒนาครับ"
    elif text == 'งานค้าง':
        # ในอนาคตจะเพิ่ม Logic การดึงข้อมูลจากฐานข้อมูล
        return "ฟังก์ชัน 'งานค้าง' กำลังอยู่ในระหว่างการพัฒนาครับ"
    return None
