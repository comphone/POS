import os
from app import create_app

# บังคับให้โปรแกรมรันในโหมด 'dev' เสมอเมื่อใช้ไฟล์นี้
# สำหรับ Production ให้ตั้งค่า FLASK_CONFIG='prod' ใน Environment Variable แทน
config_name = os.getenv('FLASK_CONFIG') or 'dev'

# สร้างแอปพลิเคชันโดยใช้ Application Factory
app = create_app(config_name)

if __name__ == '__main__':
    # รันแอปพลิเคชัน
    app.run(host='0.0.0.0', port=5001)
