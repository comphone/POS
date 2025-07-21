from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class ProductForm(FlaskForm):
    """Form for adding or editing a product/part."""
    name = StringField('ชื่อสินค้า/อะไหล่', validators=[DataRequired(), Length(min=2, max=100)])
    sku = StringField('SKU (รหัสสินค้า)', validators=[Optional(), Length(max=50)])
    description = TextAreaField('คำอธิบาย', validators=[Optional(), Length(max=500)])
    price = FloatField('ราคาขาย', validators=[DataRequired(), NumberRange(min=0)])
    stock_quantity = IntegerField('จำนวนในสต็อก', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('บันทึกข้อมูล')
