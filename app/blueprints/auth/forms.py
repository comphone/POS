from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    """
    Form for users to login.
    """
    # เราใช้ email ในการ login แทน username เพื่อความปลอดภัย
    email = StringField('Email', validators=[
        DataRequired(message='กรุณากรอกอีเมล'),
        Email(message='รูปแบบอีเมลไม่ถูกต้อง')
    ])
    
    password = PasswordField('Password', validators=[
        DataRequired(message='กรุณากรอกรหัสผ่าน')
    ])
    
    remember_me = BooleanField('จดจำฉันไว้ในระบบ')
    
    submit = SubmitField('เข้าสู่ระบบ')

