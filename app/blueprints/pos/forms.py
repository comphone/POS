from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Customer

def get_customers():
    return Customer.query.order_by(Customer.name).all()

class PosForm(FlaskForm):
    """Form for the Point of Sale terminal."""
    customer = QuerySelectField(
        'ลูกค้า',
        query_factory=get_customers,
        get_label='name',
        allow_blank=True, # อนุญาตให้เป็นลูกค้าจรได้
        blank_text='-- ลูกค้าทั่วไป --'
    )
    # เราจะใช้ HiddenField ในการเก็บข้อมูลตะกร้าสินค้า
    cart_items = HiddenField('Cart Items', validators=[DataRequired()])
    submit = SubmitField('เสร็จสิ้นการขาย')
