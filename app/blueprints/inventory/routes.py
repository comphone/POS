from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from . import inventory_bp
from .forms import ProductForm
from app import db
from app.models import Product

@inventory_bp.route('/')
@login_required
def list_products():
    products = Product.query.order_by(Product.name).all()
    return render_template('inventory/product_list.html', products=products)

@inventory_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            sku=form.sku.data,
            description=form.description.data,
            price=form.price.data,
            stock_quantity=form.stock_quantity.data
        )
        db.session.add(new_product)
        db.session.commit()
        flash('เพิ่มข้อมูลสินค้าใหม่เรียบร้อยแล้ว', 'success')
        return redirect(url_for('inventory.list_products'))
    return render_template('inventory/product_form.html', title='เพิ่มสินค้าใหม่', form=form)

@inventory_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = db.session.get(Product, id)
    if not product:
        flash('ไม่พบข้อมูลสินค้า', 'danger')
        return redirect(url_for('inventory.list_products'))
    
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.sku = form.sku.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock_quantity = form.stock_quantity.data
        db.session.commit()
        flash('แก้ไขข้อมูลสินค้าเรียบร้อยแล้ว', 'success')
        return redirect(url_for('inventory.list_products'))
        
    return render_template('inventory/product_form.html', title='แก้ไขข้อมูลสินค้า', form=form)

@inventory_bp.route('/api/search_products')
@login_required
def search_products():
    query = request.args.get('q', '', type=str)
    if not query:
        return jsonify([])

    # ค้นหาทั้งในชื่อและ SKU
    products = Product.query.filter(
        Product.name.ilike(f'%{query}%') | Product.sku.ilike(f'%{query}%')
    ).limit(10).all()

    results = [
        {
            'id': p.id,
            'name': p.name,
            'sku': p.sku,
            'price': p.price,
            'stock': p.stock_quantity
        }
        for p in products
    ]
    return jsonify(results)
