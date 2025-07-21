from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Optional

class CustomerForm(FlaskForm):
    """Form for adding or editing a customer."""
    name = StringField('ชื่อ-นามสกุล', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('เบอร์โทรศัพท์', validators=[Optional(), Length(max=20)])
    email = StringField('อีเมล', validators=[Optional(), Email()])
    address = TextAreaField('ที่อยู่', validators=[Optional(), Length(max=500)])
    submit = SubmitField('บันทึกข้อมูล')
