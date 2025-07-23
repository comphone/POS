คู่มือ: การใช้งาน Service Account Key บน Render.comเอกสารนี้คือขั้นตอนทั้งหมดในการนำ Service Account Key ที่คุณเพิ่งสร้าง ไปตั้งค่าและใช้งานบน Render.com เพื่อให้สคริปต์ย้ายข้อมูล (Data Migration) สามารถทำงานได้สำเร็จขั้นตอนที่ 1: แชร์สิทธิ์ให้ "บัญชีหุ่นยนต์" (สำคัญมาก)ตอนนี้คุณมี "บัญชีผู้ใช้สำหรับหุ่นยนต์" แล้ว แต่หุ่นยนต์ตัวนี้ยังไม่มีสิทธิ์เข้าถึงข้อมูล Google Tasks และ Google Drive ของคุณ เราต้องทำการ "แชร์" สิทธิ์ให้มันก่อน เหมือนกับที่คุณแชร์ไฟล์ให้เพื่อนร่วมงานครับคัดลอกอีเมลของ Service Account: จากไฟล์ comphone-service-app.json ที่คุณส่งมา อีเมลของ Service Account ของคุณคือ:comphone-pos@comphone-service-app.iam.gserviceaccount.comแชร์ Google Tasks:เปิด Google Tasks ของคุณที่ด้านบนของรายการ Task ของคุณ คลิกที่เมนู ... แล้วเลือก "Share list"นำอีเมลของ Service Account (จากข้อ 1) ไปวางในช่อง "Add editors" แล้วกดแชร์แชร์ Google Drive Folder:ไปที่ Google Drive ของคุณคลิกขวาที่โฟลเดอร์หลักที่คุณใช้เก็บไฟล์แนบของงานซ่อม (โฟลเดอร์ที่มี ID ตรงกับ GOOGLE_DRIVE_FOLDER_ID ของคุณ)เลือก Share > Shareนำอีเมลของ Service Account (จากข้อ 1) ไปวางในช่อง "Add people and groups", ตั้งสิทธิ์ให้เป็น Editor, แล้วกด Sendขั้นตอนที่ 2: ตั้งค่า Environment Variable บน Render.comเราจะนำ "เนื้อหา" ของไฟล์กุญแจ .json ทั้งหมด ไปตั้งเป็นค่าที่เป็นความลับบนเซิร์ฟเวอร์ของ Renderเปิดไฟล์ comphone-service-app.json ที่คุณดาวน์โหลดมาด้วยโปรแกรม Text Editor (เช่น Notepad, VS Code)คัดลอก (Copy) เนื้อหาทั้งหมด ที่อยู่ในไฟล์นั้น (ตั้งแต่ { ตัวแรก จนถึง } ตัวสุดท้าย)ไปที่ Dashboard ของ Web Service ของคุณบน Render.comไปที่เมนู "Environment"คลิก "+ Add Environment Variable" แล้วสร้างตัวแปรใหม่:Key: GOOGLE_SERVICE_ACCOUNT_JSONValue: วาง (Paste) เนื้อหาไฟล์ .json ทั้งหมด ที่คุณคัดลอกมาลงในช่องนี้กด "Save Changes"ขั้นตอนที่ 3: อัปเดตสคริปต์ migrate_from_google_tasks.pyผมได้เขียนสคริปต์เวอร์ชันใหม่ให้แล้ว โค้ดนี้ถูกออกแบบมาให้อ่านค่าจาก GOOGLE_SERVICE_ACCOUNT_JSON ที่เราเพิ่งตั้งค่าไป เพื่อใช้ในการยืนยันตัวตนแทนวิธีเก่าที่ต้องใช้เบราว์เซอร์ครับimport os
import json
import re
from datetime import datetime
from dateutil.parser import parse as date_parse
import sys

# --- Setup for running script standalone ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
load_dotenv()
# -----------------------------------------

from app import create_app, db
from app.models import Customer, User, ServiceJob, JobUpdate, ServiceJobStatus
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Configuration ---
SCOPES = ['https://www.googleapis.com/auth/tasks.readonly', 'https://www.googleapis.com/auth/drive.readonly']
GOOGLE_TASKS_LIST_ID = os.environ.get('GOOGLE_TASKS_LIST_ID', '@default') 

# --- Helper Functions (from old app.py) ---
def parse_customer_info_from_notes(notes):
    info = {'name': '', 'phone': '', 'address': ''}
    if not notes: return info
    name_match = re.search(r"ลูกค้า:\s*(.*)", notes, re.IGNORECASE)
    phone_match = re.search(r"เบอร์โทรศัพท์:\s*(.*)", notes, re.IGNORECASE)
    address_match = re.search(r"ที่อยู่:\s*(.*)", notes, re.IGNORECASE)
    if name_match: info['name'] = name_match.group(1).strip().split(':')[-1].strip()
    if phone_match: info['phone'] = phone_match.group(1).strip().split(':')[-1].strip()
    if address_match: info['address'] = address_match.group(1).strip().split(':')[-1].strip()
    return info

def parse_tech_report_from_notes(notes):
    if not notes: return [], ""
    report_blocks = re.findall(r"--- TECH_REPORT_START ---\s*\n(.*?)\n--- TECH_REPORT_END ---", notes, re.DOTALL)
    history = []
    for json_str in report_blocks:
        try:
            history.append(json.loads(json_str))
        except json.JSONDecodeError:
            print(f"  [WARNING] Failed to decode tech report JSON.")
    base_notes = re.sub(r"--- TECH_REPORT_START ---.*?--- TECH_REPORT_END ---", "", notes, flags=re.DOTALL).strip()
    return history, base_notes

# --- [แก้ไข] Main Migration Logic ---
def get_google_service_with_service_account(api_name, api_version):
    """สร้าง Service Object โดยใช้ Service Account JSON จาก Environment Variable"""
    service_account_json_str = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    if not service_account_json_str:
        raise ValueError("Environment variable 'GOOGLE_SERVICE_ACCOUNT_JSON' is not set on Render.com.")
    
    try:
        credentials_info = json.loads(service_account_json_str)
        creds = service_account.Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
        service = build(api_name, api_version, credentials=creds)
        return service
    except Exception as e:
        print(f"Error creating Google service with Service Account: {e}")
        return None

def get_all_google_tasks(service):
    tasks = []
    request = service.tasks().list(tasklist=GOOGLE_TASKS_LIST_ID, maxResults=100, showCompleted=True, showHidden=True)
    while request is not None:
        response = request.execute()
        tasks.extend(response.get('items', []))
        request = service.tasks().list_next(request, response)
    return tasks

def migrate_data():
    print("--- Starting Data Migration using Service Account ---")

    # 1. Get Google Service
    print("[1/5] Authenticating with Google Service Account...")
    try:
        tasks_service = get_google_service_with_service_account('tasks', 'v1')
        if not tasks_service:
            return
        print("      Authentication successful.")
    except Exception as e:
        print(f"[ERROR] Could not authenticate. Details: {e}")
        return

    # 2. Fetch all tasks
    print("[2/5] Fetching all tasks from Google Tasks...")
    all_tasks = get_all_google_tasks(tasks_service)
    print(f"      Found {len(all_tasks)} tasks to migrate.")

    app = create_app(os.getenv('FLASK_CONFIG') or 'dev')
    with app.app_context():
        print("[3/5] Preparing local database...")
        default_user = User.query.filter_by(role='ADMIN').first()
        if not default_user:
            print("[ERROR] Default admin user not found. Creating one...")
            # This part is a fallback, ideally the app should be run once to create the user
            admin_user = User(username='admin', email='admin@example.com', first_name='Admin', last_name='User', role='ADMIN')
            admin_user.set_password('password')
            db.session.add(admin_user)
            db.session.commit()
            default_user = admin_user
        print("      Database ready.")

        print("[4/5] Processing and inserting data...")
        for i, task_data in enumerate(all_tasks):
            print(f"  -> Processing task {i+1}/{len(all_tasks)}: {task_data.get('title')}")
            notes = task_data.get('notes', '')
            tech_reports, base_notes_text = parse_tech_report_from_notes(notes)
            customer_info = parse_customer_info_from_notes(base_notes_text)

            if not customer_info.get('name'):
                print("     [SKIPPING] Task has no customer name.")
                continue

            customer = Customer.query.filter_by(name=customer_info['name'], phone=customer_info['phone']).first()
            if not customer:
                customer = Customer(name=customer_info['name'], phone=customer_info['phone'], address=customer_info['address'])
                db.session.add(customer)
                db.session.flush()

            job_status = ServiceJobStatus.COMPLETED if task_data.get('status') == 'completed' else ServiceJobStatus.RECEIVED
            job_number = f"MIG-{task_data.get('id', i)}"
            created_at_val = date_parse(task_data.get('created')) if task_data.get('created') else datetime.utcnow()

            service_job = ServiceJob(
                job_number=job_number, title=task_data.get('title'),
                problem_description=base_notes_text, customer_id=customer.id,
                status=job_status, created_at=created_at_val
            )
            db.session.add(service_job)
            db.session.flush()

            for report in tech_reports:
                summary = report.get('work_summary', 'No summary provided.')
                try: report_date = date_parse(report.get('summary_date'))
                except: report_date = service_job.created_at
                job_update = JobUpdate(
                    service_job_id=service_job.id, author_id=default_user.id,
                    summary=summary, created_at=report_date
                )
                db.session.add(job_update)
        
        print("[5/5] Committing all changes to the database...")
        try:
            db.session.commit()
            print("      Successfully committed all data.")
        except Exception as e:
            print(f"[ERROR] An error occurred during database commit. Rolling back.")
            print(f"      Details: {e}")
            db.session.rollback()

    print("--- Data Migration Finished ---")

if __name__ == '__main__':
    migrate_data()
