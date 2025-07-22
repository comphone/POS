import os
from fpdf import FPDF
from flask import current_app
from datetime import datetime

class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # เพิ่มฟอนต์ภาษาไทย
        font_path = os.path.join(current_app.static_folder, 'fonts', 'Sarabun-Regular.ttf')
        if os.path.exists(font_path):
            self.add_font('Sarabun', '', font_path, uni=True)
        else:
            # Fallback font if Sarabun is not found
            self.add_font('helvetica', '', 'helvetica.pl')

    def header(self):
        self.set_font('Sarabun', '', 16)
        self.cell(0, 10, 'ใบเสร็จรับเงิน / Receipt', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Sarabun', '', 8)
        self.cell(0, 10, f'หน้า {self.page_no()}', 0, 0, 'C')
        
    def chapter_title(self, title):
        self.set_font('Sarabun', '', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)

    def chapter_body(self, data):
        self.set_font('Sarabun', '', 12)
        for key, value in data.items():
            self.multi_cell(0, 10, f'{key}: {value}')
        self.ln()

    def create_table(self, table_data, headers):
        self.set_font('Sarabun', '', 10)
        line_height = self.font_size * 2
        col_width = self.epw / len(headers)

        # Headers
        for header in headers:
            self.cell(col_width, line_height, header, border=1)
        self.ln(line_height)

        # Data
        for row in table_data:
            for item in row:
                self.cell(col_width, line_height, str(item), border=1)
            self.ln(line_height)
        self.ln(line_height)

def generate_receipt_pdf(sale):
    """
    สร้างไฟล์ PDF สำหรับใบเสร็จรับเงิน
    """
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ข้อมูลผู้ขาย (ควรดึงมาจาก Settings ในอนาคต)
    seller_info = {
        "บริษัท": "Comphone Integrated System",
        "ที่อยู่": "123 ถนนตัวอย่าง, กรุงเทพฯ 10110",
        "เลขประจำตัวผู้เสียภาษี": "0123456789012"
    }
    pdf.chapter_body(seller_info)

    # ข้อมูลการขายและลูกค้า
    customer_name = sale.customer.name if sale.customer else "ลูกค้าทั่วไป"
    sale_info = {
        "เลขที่ใบเสร็จ": sale.sale_number,
        "วันที่": sale.created_at.strftime('%d/%m/%Y %H:%M'),
        "ลูกค้า": customer_name,
        "พนักงานขาย": sale.salesperson.full_name
    }
    pdf.chapter_body(sale_info)

    # ตารางรายการสินค้า
    headers = ['#', 'รายการ', 'จำนวน', 'ราคา/หน่วย', 'ราคารวม']
    table_data = []
    for i, item in enumerate(sale.items):
        row = [
            i + 1,
            item.product.name,
            item.quantity,
            f"{item.price_per_unit:,.2f}",
            f"{(item.quantity * item.price_per_unit):,.2f}"
        ]
        table_data.append(row)
    
    pdf.create_table(table_data, headers)

    # สรุปยอด
    summary_data = {
        "ยอดรวม (บาท)": f"{sale.total_amount:,.2f}"
    }
    pdf.chapter_body(summary_data)

    return pdf.output(dest='S').encode('latin-1')
