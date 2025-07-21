from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from app.models import Customer, ServiceJobStatus, User, UserRole, Product

def get_customers():
    return Customer.query.order_by(Customer.name).all()

def get_technicians():
    return User.query.filter_by(role=UserRole.TECHNICIAN).order_by(User.first_name).all()

def get_products():
    return Product.query.order_by(Product.name).all()

class ServiceJobForm(FlaskForm):
    customer = QuerySelectField('ลูกค้า', query_factory=get_customers, get_label='name', allow_blank=False)
    title = StringField('ชื่องาน / อาการเสียเบื้องต้น', validators=[DataRequired(), Length(max=200)])
    problem_description = TextAreaField('รายละเอียดปัญหาที่ลูกค้าแจ้ง', validators=[DataRequired()])
    status = SelectField('สถานะงาน', choices=[(s.name, s.value) for s in ServiceJobStatus])
    submit = SubmitField('บันทึกข้อมูลงานซ่อม')

class JobUpdateForm(FlaskForm):
    summary = TextAreaField('บันทึกความคืบหน้า', validators=[DataRequired()], render_kw={"rows": 3, "placeholder": "กรอกรายละเอียดการทำงาน..."})
    submit_update = SubmitField('เพิ่มบันทึก')

# [เพิ่ม] ฟอร์มสำหรับสร้างงานย่อย
class TaskForm(FlaskForm):
    title = StringField('ชื่องานย่อย', validators=[DataRequired()], render_kw={"placeholder": "เช่น เปลี่ยนหน้าจอ, สำรองข้อมูล"})
    assignees = QuerySelectMultipleField(
        'มอบหมายให้',
        query_factory=get_technicians,
        get_label='full_name',
        widget=lambda field, **kwargs: 
            ''.join(f'<div class="form-check"><input type="checkbox" name="{field.name}" value="{val.id}" class="form-check-input"> <label class="form-check-label">{val.full_name}</label></div>' for val in field.query)
    )
    submit_task = SubmitField('เพิ่มงานย่อย')

# [เพิ่ม] ฟอร์มสำหรับเพิ่มอะไหล่
class AddPartForm(FlaskForm):
    product = QuerySelectField('สินค้า/อะไหล่', query_factory=get_products, get_label='name', allow_blank=False)
    quantity = IntegerField('จำนวน', validators=[DataRequired(), NumberRange(min=1)], default=1)
    submit_part = SubmitField('เพิ่มอะไหล่')
