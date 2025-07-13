import os
from dotenv import load_dotenv

# โหลดตัวแปรสภาพแวดล้อมจากไฟล์ .env
load_dotenv()

class Config:
    # ตั้งค่า Secret Key สำหรับ Flask (ใช้ในการรักษาความปลอดภัยของ session และ CSRF)
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # ตั้งค่าฐานข้อมูล SQLite
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    # ใช้ instance_path เพื่อให้ไฟล์ .db อยู่ในโฟลเดอร์ instance
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'instance', 'app.db')

    SQLALCHEMY_TRACK_MODIFICATIONS = False # ปิดการติดตามการเปลี่ยนแปลงของ SQLAlchemy (ประหยัดทรัพยากร)

    # ตั้งค่าสำหรับ LINE Messaging API (เฟส 3)
    LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
    LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
    # User ID หรือ Group ID ที่จะใช้ส่งข้อความแจ้งเตือน (ต้องหามาเองจากการตั้งค่า LINE Developers)
    LINE_USER_ID_FOR_NOTIFICATIONS = os.environ.get('LINE_USER_ID_FOR_NOTIFICATIONS')

