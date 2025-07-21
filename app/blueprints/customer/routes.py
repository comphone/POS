from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from . import customer_bp
from .forms import CustomerForm
from app import db
from app.models import Customer

@customer_bp.route('/')
@login_required
def list_customers():
    customers = Customer.query.order_by(Customer.name).all()
    return render_template('customer/customer_list.html', customers=customers)

@customer_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        new_customer = Customer(
            name=form.name.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data
        )
        db.session.add(new_customer)
        db.session.commit()
        flash('เพิ่มข้อมูลลูกค้าใหม่เรียบร้อยแล้ว', 'success')
        return redirect(url_for('customer.list_customers'))
    return render_template('customer/customer_form.html', title='เพิ่มลูกค้าใหม่', form=form)

@customer_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    customer = db.session.get(Customer, id)
    if not customer:
        flash('ไม่พบข้อมูลลูกค้า', 'danger')
        return redirect(url_for('customer.list_customers'))
    
    form = CustomerForm(obj=customer)
    if form.validate_on_submit():
        customer.name = form.name.data
        customer.phone = form.phone.data
        customer.email = form.email.data
        customer.address = form.address.data
        db.session.commit()
        flash('แก้ไขข้อมูลลูกค้าเรียบร้อยแล้ว', 'success')
        return redirect(url_for('customer.list_customers'))
        
    return render_template('customer/customer_form.html', title='แก้ไขข้อมูลลูกค้า', form=form)
