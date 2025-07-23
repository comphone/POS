from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Customer, ServiceJobStatus, User, UserRole, Product

def get_customers():
    return Customer.query.order_by(Customer.name).all()

def get_technicians():
    # ในอนาคตเราสามารถกรอง User ที่เป็นช่างจริงๆ ได้
    return User.query.order_by(User.first_name).all()

def get_products():
    return Product.query.order_by(Product.name).all()

class ServiceJobForm(FlaskForm):
    """
    Form สำหรับสร้างและแก้ไขข้อมูลหลักของใบงานซ่อม
    อ้างอิงจาก form.html เดิม
    """
    customer = QuerySelectField(
        'ลูกค้า',
        query_factory=get_customers,
        get_label='name',
        allow_blank=False,
        validators=[DataRequired(message="กรุณาเลือกลูกค้า")]
    )
    title = StringField('ชื่องาน / อาการเสียเบื้องต้น', validators=[DataRequired(), Length(max=200)])
    problem_description = TextAreaField('รายละเอียดปัญหาที่ลูกค้าแจ้ง', validators=[DataRequired()])
    status = SelectField('สถานะงาน', choices=[(s.name, s.value) for s in ServiceJobStatus])
    
    # Fields from old form.html
    organization_name = StringField('ชื่อหน่วยงาน/บริษัท (ถ้ามี)')
    map_url = StringField('พิกัดแผนที่ (Google Maps URL)')

    submit = SubmitField('บันเทึกข้อมูล')

class JobUpdateForm(FlaskForm):
    """
    Form สำหรับบันทึกความคืบหน้า (Progress Report)
    """
    summary = TextAreaField('บันทึกความคืบหน้า', validators=[DataRequired()], render_kw={"rows": 3, "placeholder": "กรอกรายละเอียดการทำงาน..."})
    # เพิ่ม Hidden Field สำหรับเก็บข้อมูลช่าง
    technicians = HiddenField('ช่างผู้รับผิดชอบ', validators=[DataRequired(message="กรุณาเลือกช่างผู้รับผิดชอบ")])
    submit_update = SubmitField('เพิ่มบันทึก')

class TaskForm(FlaskForm):
    """
    Form สำหรับสร้างงานย่อย (Task)
    """
    title = StringField('ชื่องานย่อย', validators=[DataRequired()], render_kw={"placeholder": "เช่น เปลี่ยนหน้าจอ, สำรองข้อมูล"})
    submit_task = SubmitField('เพิ่มงานย่อย')

class AddPartForm(FlaskForm):
    """
    Form สำหรับเพิ่มอะไหล่ที่ใช้
    """
    product = QuerySelectField('สินค้า/อะไหล่', query_factory=get_products, get_label='name', allow_blank=False)
    quantity = IntegerField('จำนวน', validators=[DataRequired(), NumberRange(min=1)], default=1)
    submit_part = SubmitField('เพิ่มอะไหล่')

class RescheduleForm(FlaskForm):
    """
    Form สำหรับเลื่อนนัดหมาย
    """
    reschedule_due = StringField('กำหนดวันนัดหมายใหม่', validators=[DataRequired()], render_kw={'type': 'datetime-local'})
    reschedule_reason = TextAreaField('เหตุผลที่เลื่อนนัด / ปัญหาที่พบ', validators=[Optional()], render_kw={"rows": 3, "placeholder": "เช่น ลูกค้าขอเลื่อน, รออะไหล่"})
    technicians = HiddenField('ผู้บันทึกการเลื่อนนัด', validators=[DataRequired(message="กรุณาเลือกผู้บันทึก")])
    submit_reschedule = SubmitField('บันทึกการเลื่อนนัด')

class CompleteJobForm(FlaskForm):
    """
    Form สำหรับปิดงาน
    """
    summary = TextAreaField('สรุปงานที่ทำ', validators=[DataRequired()], render_kw={"rows": 3, "placeholder": "เช่น ติดตั้งเรียบร้อย ทดสอบระบบใช้งานได้ปกติ"})
    technicians = HiddenField('ช่างผู้รับผิดชอบ', validators=[DataRequired(message="กรุณาเลือกช่างผู้รับผิดชอบ")])
    submit_complete = SubmitField('ยืนยันการปิดงาน')
