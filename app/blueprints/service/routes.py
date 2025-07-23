from flask import render_template, redirect, url_for, flash, request, jsonify, Response
from flask_login import login_required, current_user
from . import service_bp
from .forms import ServiceJobForm, JobUpdateForm, TaskForm, AddPartForm, RescheduleForm, CompleteJobForm
from app import db
from app.models import ServiceJob, ServiceJobStatus, JobUpdate, Task, ServiceJobPart, Product, User, Customer
import random
import string
import qrcode
from io import BytesIO
import base64
from datetime import datetime
import pytz

THAILAND_TZ = pytz.timezone('Asia/Bangkok')

@service_bp.route('/')
@login_required
def list_jobs():
    jobs = ServiceJob.query.order_by(ServiceJob.created_at.desc()).all()
    return render_template('service/service_list.html', jobs=jobs)

def generate_job_number():
    prefix = 'SRV'
    while True:
        suffix = ''.join(random.choices(string.digits, k=6))
        job_num = f"{prefix}{suffix}"
        if not ServiceJob.query.filter_by(job_number=job_num).first():
            return job_num

@service_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_job():
    form = ServiceJobForm()
    if form.validate_on_submit():
        new_job = ServiceJob(
            job_number=generate_job_number(),
            customer_id=form.customer.data.id,
            title=form.title.data,
            problem_description=form.problem_description.data,
            status=ServiceJobStatus[form.status.data]
        )
        db.session.add(new_job)
        db.session.commit()
        flash('เปิดใบงานซ่อมใหม่เรียบร้อยแล้ว', 'success')
        return redirect(url_for('service.job_detail', job_id=new_job.id))
    
    return render_template('service/service_form.html', title='เปิดใบงานซ่อมใหม่', form=form)

@service_bp.route('/<int:job_id>', methods=['GET', 'POST'])
@login_required
def job_detail(job_id):
    job = db.session.get(ServiceJob, job_id)
    if not job:
        flash('ไม่พบงานซ่อมที่ระบุ', 'danger')
        return redirect(url_for('service.list_jobs'))

    update_form = JobUpdateForm()
    task_form = TaskForm()
    part_form = AddPartForm()
    reschedule_form = RescheduleForm()
    complete_form = CompleteJobForm()
    
    # Pre-populate technician fields for modals
    technician_list = User.query.all() # In future, filter by role

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'submit_update' and update_form.validate_on_submit():
            new_update = JobUpdate(service_job=job, author=current_user, summary=update_form.summary.data)
            db.session.add(new_update)
            db.session.commit()
            flash('เพิ่มบันทึกความคืบหน้าเรียบร้อยแล้ว', 'success')
            return redirect(url_for('service.job_detail', job_id=job.id))

        if action == 'submit_task' and task_form.validate_on_submit():
            new_task = Task(service_job=job, title=task_form.title.data)
            db.session.add(new_task)
            db.session.commit()
            flash('เพิ่มงานย่อยเรียบร้อยแล้ว', 'success')
            return redirect(url_for('service.job_detail', job_id=job.id))

        if action == 'submit_part' and part_form.validate_on_submit():
            # ... (Logic for adding part is the same) ...
            pass
        
        if action == 'submit_reschedule' and reschedule_form.validate_on_submit():
            due_str = reschedule_form.reschedule_due.data
            dt_local = THAILAND_TZ.localize(datetime.fromisoformat(due_str))
            job.due_date = dt_local.astimezone(pytz.utc)
            job.status = ServiceJobStatus.IN_PROGRESS
            # Create a JobUpdate for reschedule event
            reason = reschedule_form.reschedule_reason.data
            technicians = reschedule_form.technicians.data
            summary = f"เลื่อนนัดหมายเป็น: {dt_local.strftime('%d/%m/%Y %H:%M')}\nเหตุผล: {reason}\nผู้บันทึก: {technicians}"
            new_update = JobUpdate(service_job=job, author=current_user, summary=summary)
            db.session.add(new_update)
            db.session.commit()
            flash('เลื่อนนัดหมายเรียบร้อยแล้ว', 'success')
            return redirect(url_for('service.job_detail', job_id=job.id))

        if action == 'submit_complete' and complete_form.validate_on_submit():
            job.status = ServiceJobStatus.COMPLETED
            job.completed_at = datetime.now(pytz.utc)
            # Create a final JobUpdate
            summary = complete_form.summary.data
            technicians = complete_form.technicians.data
            final_summary = f"**ปิดงาน**\nสรุปงาน: {summary}\nช่างผู้รับผิดชอบ: {technicians}"
            new_update = JobUpdate(service_job=job, author=current_user, summary=final_summary)
            db.session.add(new_update)
            db.session.commit()
            flash('ปิดงานเรียบร้อยแล้ว!', 'success')
            return redirect(url_for('service.job_detail', job_id=job.id))

    return render_template('service/service_detail.html', 
                           job=job, 
                           update_form=update_form,
                           task_form=task_form, 
                           part_form=part_form,
                           reschedule_form=reschedule_form,
                           complete_form=complete_form,
                           technician_list=technician_list)

# ... (edit_job, toggle_task, delete_task, delete_part routes are mostly the same) ...

# [เพิ่ม] Route สำหรับสร้าง QR Code
@service_bp.route('/qr/onboarding/<int:job_id>')
@login_required
def generate_customer_onboarding_qr(job_id):
    job = db.session.get(ServiceJob, job_id)
    if not job:
        abort(404)
    
    # This URL should point to a future LIFF app page
    onboarding_url = url_for('customer.view', id=job.customer_id, _external=True) 
    
    # Generate QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(onboarding_url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    return render_template('service/generate_qr.html', 
                           title=f"QR Code สำหรับลูกค้า: {job.customer.name}",
                           qr_code_base64=img_str,
                           job=job)
