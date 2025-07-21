# ===================================================================
# File: app/blueprints/accounting/routes.py
# ===================================================================
from flask import render_template
from flask_login import login_required
from . import accounting_bp
from app.models import Sale

@accounting_bp.route('/')
@login_required
def sale_history():
    sales = Sale.query.order_by(Sale.created_at.desc()).all()
    return render_template('accounting/sale_list.html', sales=sales)