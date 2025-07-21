# ===================================================================
# File: app/blueprints/pos/routes.py
# ===================================================================
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import pos_bp
from .forms import PosForm
from app import db
from app.models import Sale, SaleItem, Product, Customer
import json
import random
import string

def generate_sale_number():
    prefix = 'SAL'
    while True:
        suffix = ''.join(random.choices(string.digits, k=8))
        sale_num = f"{prefix}{suffix}"
        if not Sale.query.filter_by(sale_number=sale_num).first():
            return sale_num

@pos_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = PosForm()
    
    if form.validate_on_submit():
        try:
            cart_data = json.loads(form.cart_items.data)
            if not cart_data:
                flash('กรุณาเพิ่มสินค้าลงในตะกร้าก่อน', 'warning')
                return redirect(url_for('pos.index'))

            total_amount = sum(item['qty'] * item['price'] for item in cart_data)

            new_sale = Sale(
                sale_number=generate_sale_number(),
                customer_id=form.customer.data.id if form.customer.data else None,
                salesperson_id=current_user.id,
                total_amount=total_amount
            )
            db.session.add(new_sale)
            
            for item_data in cart_data:
                product = db.session.get(Product, item_data['id'])
                if not product or product.stock_quantity < item_data['qty']:
                    raise Exception(f"สินค้า '{item_data['name']}' ไม่เพียงพอในสต็อก")

                product.stock_quantity -= item_data['qty']
                
                sale_item = SaleItem(
                    sale=new_sale,
                    product_id=product.id,
                    quantity=item_data['qty'],
                    price_per_unit=item_data['price']
                )
                db.session.add(sale_item)

            db.session.commit()
            flash(f'บันทึกการขาย #{new_sale.sale_number} สำเร็จ!', 'success')
            return redirect(url_for('pos.index'))

        except Exception as e:
            db.session.rollback()
            flash(f'เกิดข้อผิดพลาดในการบันทึกการขาย: {e}', 'danger')

    return render_template('pos/pos_terminal.html', form=form)