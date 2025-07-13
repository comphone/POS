# comphone/utils/line_api.py
from linebot import LineBotApi
from linebot.models import TextSendMessage
from flask import current_app # ใช้ current_app เพื่อเข้าถึง config ภายใน application context

def send_line_message(message_text, target_id=None):
    """
    ส่งข้อความผ่าน LINE Messaging API ไปยัง User ID หรือ Group ID ที่กำหนด
    หรือไปยัง LINE_USER_ID_FOR_NOTIFICATIONS ที่ตั้งค่าไว้ใน config.

    Args:
        message_text (str): ข้อความที่จะส่ง
        target_id (str, optional): User ID หรือ Group ID ที่ต้องการส่งข้อความไปหา.
                                   หากไม่ระบุ จะใช้ LINE_USER_ID_FOR_NOTIFICATIONS จาก config.
    Returns:
        bool: True หากส่งสำเร็จ, False หากเกิดข้อผิดพลาด.
    """
    try:
        # ตรวจสอบว่ามี LINE API Token และ Secret ถูกตั้งค่าหรือไม่
        if not current_app.config.get('LINE_CHANNEL_ACCESS_TOKEN'):
            print("LINE_CHANNEL_ACCESS_TOKEN ไม่ได้ถูกตั้งค่าใน config. ไม่สามารถส่ง LINE Message ได้.")
            return False

        line_bot_api = LineBotApi(current_app.config['LINE_CHANNEL_ACCESS_TOKEN'])

        # กำหนด ID ผู้รับ
        if target_id:
            recipient_id = target_id
        else:
            recipient_id = current_app.config.get('LINE_USER_ID_FOR_NOTIFICATIONS')

        if not recipient_id:
            print("ไม่พบ LINE User ID หรือ Group ID สำหรับการแจ้งเตือน. ไม่สามารถส่ง LINE Message ได้.")
            return False

        # ส่งข้อความ
        line_bot_api.push_message(recipient_id, TextSendMessage(text=message_text))
        print(f"LINE message sent to {recipient_id}: {message_text}")
        return True
    except Exception as e:
        print(f"Failed to send LINE message to {recipient_id}: {e}")
        return False

