# comphone_pos/comphone/core/routes.py (ฉบับอัปเดตสมบูรณ์)

from flask import render_template, flash, redirect, url_for, request, current_app, send_file
from flask_login import login_required
import sqlalchemy as sa
from comphone import db
from comphone.core import bp
from comphone.core.forms import CustomerForm
from comphone.models import Customer, Product, Sale
from comphone.decorators import admin_required # Import decorator สำหรับ Admin
from datetime import datetime
import os

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    """
    หน้า Dashboard หลัก
    Endpoint: core.index
    """
    try:
        customer_count = db.session.query(Customer.id).count()
        product_count = db.session.query(Product.id).count()
        sales_total = db.session.query(sa.func.sum(Sale.total_amount)).scalar() or 0.0
    except Exception as e:
        customer_count = 0
        product_count = 0
        sales_total = 0.0
        print(f"Error querying dashboard stats: {e}")

    return render_template('core/dashboard.html', title='Dashboard',
                           customer_count=customer_count,
                           product_count=product_count,
                           sales_total=sales_total)

@bp.route('/customers')
@login_required
def customers():
    """
    หน้ารายชื่อลูกค้า พร้อมระบบแบ่งหน้า (Pagination)
    Endpoint: core.customers
    """
    page = request.args.get('page', 1, type=int)
    customers_pagination = db.paginate(
        sa.select(Customer).order_by(Customer.name),
        page=page, per_page=10, error_out=False
    )
    return render_template('core/customer_list.html', title='รายชื่อลูกค้า', customers=customers_pagination)


@bp.route('/customer/new', methods=['GET', 'POST'])
@login_required
def create_customer():
    """
    หน้าฟอร์มสำหรับสร้างลูกค้าใหม่
    Endpoint: core.create_customer
    """
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(name=form.name.data, phone=form.phone.data, address=form.address.data)
        db.session.add(customer)
        db.session.commit()
        flash('เพิ่มข้อมูลลูกค้าเรียบร้อยแล้ว!', 'success')
        return redirect(url_for('core.customers'))
    # แก้ไข: ชี้ไปที่ template ฟอร์มใหม่ที่ไม่มีการวนลูป customers
    return render_template('core/customer_create_edit_form.html', form=form, title='เพิ่มลูกค้าใหม่')


@bp.route('/customer/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    """
    หน้าฟอร์มสำหรับแก้ไขข้อมูลลูกค้า
    Endpoint: core.edit_customer
    """
    customer = db.get_or_404(Customer, id)
    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        customer.name = form.name.data
        customer.phone = form.phone.data
        customer.address = form.address.data
        db.session.commit()
        flash('แก้ไขข้อมูลลูกค้าเรียบร้อยแล้ว', 'success')
        return redirect(url_for('core.customers'))
    # แก้ไข: ชี้ไปที่ template ฟอร์มใหม่ที่ไม่มีการวนลูป customers
    return render_template('core/customer_create_edit_form.html', form=form, title='แก้ไขข้อมูลลูกค้า')


@bp.route('/customer/<int:id>/delete', methods=['POST'])
@login_required
def delete_customer(id):
    """
    ฟังก์ชันสำหรับลบข้อมูลลูกค้า
    Endpoint: core.delete_customer
    """
    customer = db.get_or_404(Customer, id)
    db.session.delete(customer)
    db.session.commit()
    flash('ลบข้อมูลลูกค้าเรียบร้อยแล้ว', 'info')
    return redirect(url_for('core.customers'))

# --- ฟังก์ชันใหม่สำหรับสำรองข้อมูล ---
@bp.route('/backup/db')
@login_required
@admin_required # เฉพาะ admin เท่านั้นที่ backup ได้
def backup_db():
    """
    ดาวน์โหลดไฟล์ฐานข้อมูล SQLite ทั้งหมด
    Endpoint: core.backup_db
    """
    try:
        # หา path ของไฟล์ .db จาก config
        db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')

        # ตรวจสอบว่าไฟล์มีอยู่จริง
        if not os.path.isabs(db_path):
            db_path = os.path.join(current_app.instance_path, db_path)
            # ในกรณีที่ path ไม่ใช่ absolute path ให้ join กับ instance_path

        if not os.path.exists(db_path):
            flash('ไม่พบไฟล์ฐานข้อมูล', 'danger')
            return redirect(url_for('core.index'))

        # ส่งไฟล์ให้ผู้ใช้ดาวน์โหลด
        return send_file(db_path, as_attachment=True,
                         download_name=f'comphone_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')

    except Exception as e:
        flash(f'เกิดข้อผิดพลาดในการสำรองข้อมูล: {e}', 'danger')
        return redirect(url_for('core.index'))
