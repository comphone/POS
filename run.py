import os
from app import create_app
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env เข้าสู่ environment variables
load_dotenv()

# [แก้ไข] บังคับให้โปรแกรมรันในโหมด 'dev' เสมอเมื่อใช้ไฟล์นี้
# นี่คือการแก้ไขที่สำคัญที่สุดสำหรับปัญหาของคุณ
config_name = 'dev'

# สร้างแอปพลิเคชันโดยใช้ Application Factory
app = create_app(config_name)

if __name__ == '__main__':
    # รันแอปพลิเคชัน
    app.run(host='0.0.0.0', port=5001)
