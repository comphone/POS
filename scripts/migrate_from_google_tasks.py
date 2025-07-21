import os
import json
import re
from datetime import datetime
from dateutil.parser import parse as date_parse

# --- Setup for running script standalone ---
# This allows the script to import modules from the main app
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# -----------------------------------------

from app import create_app, db
from app.models import Customer, User, ServiceJob, JobUpdate, Product, ServiceJobStatus, JobUpdateType
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Configuration ---
SCOPES = ['https://www.googleapis.com/auth/tasks.readonly']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'
# ใช้ ID ของ Task List จาก .env หรือใส่ค่าตรงๆ ที่นี่
GOOGLE_TASKS_LIST_ID = os.environ.get('GOOGLE_TASKS_LIST_ID', '@default') 

# --- Helper Functions for Parsing (from old app.py) ---
def parse_customer_info_from_notes(notes):
    info = {'name': '', 'phone': '', 'address': '', 'organization': ''}
    if not notes: return info

    org_match = re.search(r"หน่วยงาน:\s*(.*)", notes, re.IGNORECASE)
    name_match = re.search(r"ลูกค้า:\s*(.*)", notes, re.IGNORECASE)
    phone_match = re.search(r"เบอร์โทรศัพท์:\s*(.*)", notes, re.IGNORECASE)
    address_match = re.search(r"ที่อยู่:\s*(.*)", notes, re.IGNORECASE)

    if org_match: info['organization'] = org_match.group(1).strip()
    if name_match: info['name'] = name_match.group(1).strip()
    if phone_match: info['phone'] = phone_match.group(1).strip()
    if address_match: info['address'] = address_match.group(1).strip()
    
    # Clean up common prefixes
    for key in info:
        if ':' in info[key]:
            info[key] = info[key].split(':', 1)[-1].strip()
            
    return info

def parse_tech_report_from_notes(notes):
    if not notes: return [], ""
    report_blocks = re.findall(r"--- TECH_REPORT_START ---\s*\n(.*?)\n--- TECH_REPORT_END ---", notes, re.DOTALL)
    history = []
    for json_str in report_blocks:
        try:
            report_data = json.loads(json_str)
            history.append(report_data)
        except json.JSONDecodeError:
            print(f"  [WARNING] Failed to decode tech report JSON.")
    
    base_notes = re.sub(r"--- TECH_REPORT_START ---.*?--- TECH_REPORT_END ---", "", notes, flags=re.DOTALL).strip()
    return history, base_notes

# --- Main Migration Logic ---
def get_google_credentials():
    """Gets valid user credentials from storage or initiates the OAuth2 flow."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds

def get_all_google_tasks(service):
    """Fetches all tasks from the specified task list."""
    tasks = []
    request = service.tasks().list(tasklist=GOOGLE_TASKS_LIST_ID, maxResults=100, showCompleted=True, showHidden=True)
    while request is not None:
        response = request.execute()
        tasks.extend(response.get('items', []))
        request = service.tasks().list_next(request, response)
    return tasks

def migrate_data():
    """Main function to perform the data migration."""
    print("--- Starting Data Migration from Google Tasks ---")

    # 1. Get Google Credentials
    print("[1/5] Authenticating with Google...")
    try:
        creds = get_google_credentials()
        tasks_service = build('tasks', 'v1', credentials=creds)
        print("      Authentication successful.")
    except Exception as e:
        print(f"[ERROR] Could not authenticate with Google. Please check your '{CREDENTIALS_FILE}'.")
        print(f"      Details: {e}")
        return

    # 2. Fetch all tasks
    print("[2/5] Fetching all tasks from Google Tasks...")
    try:
        all_tasks = get_all_google_tasks(tasks_service)
        print(f"      Found {len(all_tasks)} tasks to migrate.")
    except HttpError as e:
        print(f"[ERROR] Could not fetch tasks from Google API.")
        print(f"      Details: {e}")
        return

    # Create Flask app context to work with the database
    app = create_app(os.getenv('FLASK_CONFIG') or 'dev')
    with app.app_context():
        
        # 3. Prepare local database
        print("[3/5] Preparing local database...")
        # Get the default admin user to assign as author for migrated data
        default_user = User.query.filter_by(email='admin@example.com').first()
        if not default_user:
            print("[ERROR] Default admin user not found. Please run the main app once to create it.")
            return
        
        migrated_customers = {} # Cache for customers: (name, phone) -> Customer object
        print("      Database ready.")

        # 4. Process and insert data
        print("[4/5] Processing and inserting data into the database...")
        for i, task_data in enumerate(all_tasks):
            print(f"  -> Processing task {i+1}/{len(all_tasks)}: {task_data.get('title')}")

            # Parse data from notes
            notes = task_data.get('notes', '')
            tech_reports, base_notes_text = parse_tech_report_from_notes(notes)
            customer_info = parse_customer_info_from_notes(base_notes_text)

            if not customer_info.get('name'):
                print("     [SKIPPING] Task has no customer name.")
                continue

            # Find or Create Customer
            customer_key = (customer_info['name'].lower(), customer_info['phone'])
            customer = migrated_customers.get(customer_key)
            if not customer:
                customer = Customer.query.filter_by(name=customer_info['name'], phone=customer_info['phone']).first()
                if not customer:
                    customer = Customer(
                        name=customer_info['name'],
                        phone=customer_info['phone'],
                        address=customer_info['address']
                    )
                    db.session.add(customer)
                    # We need the ID, so we flush to get it
                    db.session.flush() 
                migrated_customers[customer_key] = customer

            # Create ServiceJob
            job_status = ServiceJobStatus.COMPLETED if task_data.get('status') == 'completed' else ServiceJobStatus.RECEIVED
            
            # Use a placeholder for job number for now
            job_number = f"MIG-{task_data.get('id', i)}"

            service_job = ServiceJob(
                job_number=job_number,
                title=task_data.get('title'),
                problem_description=base_notes_text,
                customer_id=customer.id,
                status=job_status,
                created_at=date_parse(task_data.get('created'))
            )
            db.session.add(service_job)
            db.session.flush() # Get ID for JobUpdates

            # Create JobUpdates from tech reports
            for report in tech_reports:
                summary = report.get('work_summary', 'No summary provided.')
                try:
                    report_date = date_parse(report.get('summary_date'))
                except (ValueError, TypeError):
                    report_date = service_job.created_at

                job_update = JobUpdate(
                    service_job_id=service_job.id,
                    author_id=default_user.id, # Assign to default user
                    summary=summary,
                    created_at=report_date
                )
                db.session.add(job_update)

        # 5. Commit all changes
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
