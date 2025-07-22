# Comphone Integrated System

**Comphone Integrated System** คือระบบบริหารจัดการร้านซ่อมและขายสินค้าแบบครบวงจร ที่ถูกพัฒนาขึ้นโดยการรีแฟคเตอร์และผสานระบบระหว่าง `line-tasks-auto` และ `comphone_integrated` ด้วยสถาปัตยกรรม Flask Blueprints ที่ทันสมัย, ง่ายต่อการบำรุงรักษา, และพร้อมสำหรับการขยายความสามารถในอนาคต

---

## ✨ คุณสมบัติหลัก (Features)

- **ระบบจัดการงานซ่อม:** เปิดใบงาน, บันทึกความคืบหน้า, จัดการงานย่อย, และบันทึกการใช้อะไหล่พร้อมตัดสต็อก
- **ระบบขายหน้าร้าน (POS):** หน้าจอสำหรับบันทึกการขาย, ค้นหาสินค้า, และเชื่อมต่อกับฐานข้อมูลลูกค้า
- **ระบบจัดการข้อมูลพื้นฐาน:** จัดการข้อมูลลูกค้า (CRM) และคลังสินค้า (Inventory)
- **ระบบบัญชีเบื้องต้น:** ดูประวัติการขายย้อนหลังทั้งหมด
- **การเชื่อมต่อ LINE:** Webhook พื้นฐานสำหรับรับคำสั่งจาก LINE Bot
- **ระบบสมาชิกและความปลอดภัย:** ระบบล็อกอินสำหรับพนักงาน พร้อมระบบป้องกัน CSRF

---

## 🚀 การติดตั้งและเริ่มต้นใช้งาน (Getting Started)

### สิ่งที่ต้องมี (Prerequisites)

- Python 3.10+
- pip

### ขั้นตอนการติดตั้ง

1.  **Clone a repository:**
    ```bash
    git clone <your-repository-url>
    cd comphone-pos
    ```

2.  **สร้างและเปิดใช้งาน Virtual Environment:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **ติดตั้ง Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **ตั้งค่า Environment Variables:**
    - สร้างไฟล์ `.env` ในไดเรกทอรีหลัก
    - คัดลอกเนื้อหาด้านล่างไปวางในไฟล์ `.env` แล้วแก้ไขค่าต่างๆ ให้เป็นของคุณ:
    ```env
    # Flask Settings - ควรใช้ค่าที่สุ่มขึ้นมาและคาดเดายาก
    SECRET_KEY='your_super_strong_random_secret_key_here'
    WTF_CSRF_SECRET_KEY='another_very_strong_random_csrf_key'

    # LINE Bot API Credentials (ใส่ค่าจริงของคุณ)
    LINE_CHANNEL_SECRET='YOUR_REAL_LINE_CHANNEL_SECRET'
    LINE_CHANNEL_ACCESS_TOKEN='YOUR_REAL_LINE_CHANNEL_ACCESS_TOKEN'

    # Database URL (สำหรับ Production, เช่น PostgreSQL บน Render.com)
    # DATABASE_URL='postgresql://user:password@host:port/database'
    ```

---

## 🏃 การรันโปรเจกต์

### สำหรับการพัฒนา (Development)

รันคำสั่งต่อไปนี้ใน Terminal:
```bash
python run.py