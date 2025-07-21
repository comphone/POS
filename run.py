import os
from app import create_app

# [แก้ไข] กำหนดค่า config_name เป็น 'dev' โดยตรง
# เพื่อให้แน่ใจว่าโปรแกรมจะรันในโหมด Development เสมอเมื่อใช้ไฟล์นี้
config_name = 'dev'

# สร้างแอปพลิเคชันโดยใช้ Application Factory
app = create_app(config_name)

if __name__ == '__main__':
    # รันแอปพลิเคชัน
    # host='0.0.0.0' ทำให้สามารถเข้าถึงจากเครื่องอื่นในเครือข่ายเดียวกันได้
    app.run(host='0.0.0.0', port=5001)
