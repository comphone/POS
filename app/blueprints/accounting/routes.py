from flask import render_template, Response
from flask_login import login_required
from . import accounting_bp
from app.models import Sale
from app.utils import generate_receipt_pdf

@accounting_bp.route('/')
@login_required
def sale_history():
    sales = Sale.query.order_by(Sale.created_at.desc()).all()
    return render_template('accounting/sale_list.html', sales=sales)

@accounting_bp.route('/receipt/<int:sale_id>/pdf')
@login_required
def receipt_pdf(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    pdf_data = generate_receipt_pdf(sale)
    
    return Response(pdf_data,
                    mimetype='application/pdf',
                    headers={'Content-Disposition': f'attachment;filename=receipt_{sale.sale_number}.pdf'})
