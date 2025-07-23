import os
from fpdf import FPDF
from flask import current_app
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# --- PDF Generation Utility ---

class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        font_path = os.path.join(current_app.static_folder, 'fonts', 'Sarabun-Regular.ttf')
        if os.path.exists(font_path):
            self.add_font('Sarabun', '', font_path)
            self.set_font('Sarabun', '', 12)
        else:
            self.set_font('helvetica', '', 12)

    def header(self):
        self.set_font('Sarabun', '', 20)
        self.cell(0, 10, 'ใบเสร็จรับเงิน / Receipt', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Sarabun', '', 8)
        self.cell(0, 10, f'หน้า {self.page_no()}', 0, 0, 'C')

    def customer_details(self, sale):
        self.set_font('Sarabun', '', 12)
        customer_name = sale.customer.name if sale.customer else "ลูกค้าทั่วไป"
        self.cell(0, 7, f"เลขที่ใบเสร็จ: {sale.sale_number}", ln=True)
        self.cell(0, 7, f"วันที่: {sale.created_at.strftime('%d/%m/%Y %H:%M')}", ln=True)
        self.cell(0, 7, f"ลูกค้า: {customer_name}", ln=True)
        self.cell(0, 7, f"พนักงานขาย: {sale.salesperson.full_name}", ln=True)
        self.ln(10)

    def items_table(self, sale):
        self.set_font('Sarabun', '', 12)
        # Header
        self.cell(100, 10, 'รายการ', 1, 0, 'C')
        self.cell(30, 10, 'จำนวน', 1, 0, 'C')
        self.cell(30, 10, 'ราคา/หน่วย', 1, 0, 'C')
        self.cell(30, 10, 'ราคารวม', 1, 1, 'C')
        # Items
        for item in sale.items:
            self.cell(100, 10, item.product.name, 1)
            self.cell(30, 10, str(item.quantity), 1, 0, 'C')
            self.cell(30, 10, f"{item.price_per_unit:,.2f}", 1, 0, 'R')
            self.cell(30, 10, f"{(item.quantity * item.price_per_unit):,.2f}", 1, 1, 'R')
        # Total
        self.set_font('Sarabun', '', 14)
        self.cell(160, 10, 'ยอดรวมทั้งสิ้น (บาท)', 1, 0, 'R')
        self.cell(30, 10, f"{sale.total_amount:,.2f}", 1, 1, 'R')


def generate_receipt_pdf(sale):
    pdf = PDF()
    pdf.add_page()
    pdf.customer_details(sale)
    pdf.items_table(sale)
    return pdf.output(dest='S').encode('latin-1')

# --- Google API Utility ---

SCOPES = ['https://www.googleapis.com/auth/tasks', 'https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_google_credentials():
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

def get_google_service(api_name, api_version):
    try:
        creds = get_google_credentials()
        service = build(api_name, api_version, credentials=creds)
        return service
    except Exception as e:
        current_app.logger.error(f"Failed to build Google service '{api_name}': {e}")
        return None
