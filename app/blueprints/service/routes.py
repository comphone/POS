from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from . import service_bp
from .forms import ServiceJobForm, JobUpdateForm, TaskForm, AddPartForm
from app import db
from app.models import ServiceJob, ServiceJobStatus, JobUpdate, Task, ServiceJobPart, Product, User
import random
import string

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

    if request.method == 'POST':
        if update_form.submit_update.data and update_form.validate():
            new_update = JobUpdate(service_job=job, author=current_user, summary=update_form.summary.data)
            db.session.add(new_update)
            db.session.commit()
            flash('เพิ่มบันทึกความคืบหน้าเรียบร้อยแล้ว', 'success')
            return redirect(url_for('service.job_detail', job_id=job.id))

        if task_form.submit_task.data and task_form.validate():
            new_task = Task(service_job=job, title=task_form.title.data)
            db.session.add(new_task)
            db.session.commit()
            flash('เพิ่มงานย่อยเรียบร้อยแล้ว', 'success')
            return redirect(url_for('service.job_detail', job_id=job.id))

        if part_form.submit_part.data and part_form.validate():
            product = part_form.product.data
            quantity = part_form.quantity.data
            
            if product.stock_quantity < quantity:
                flash(f'สินค้า "{product.name}" มีไม่พอในสต็อก (มี: {product.stock_quantity})', 'danger')
            else:
                new_part = ServiceJobPart(
                    service_job=job, product=product, quantity=quantity,
                    price_at_time=product.price, adder=current_user
                )
                product.stock_quantity -= quantity
                db.session.add(new_part)
                db.session.commit()
                flash(f'เพิ่มการใช้อะไหล่ "{product.name}" จำนวน {quantity} ชิ้นเรียบร้อยแล้ว', 'success')
                return redirect(url_for('service.job_detail', job_id=job.id))

    return render_template('service/service_detail.html', 
                           job=job, update_form=update_form,
                           task_form=task_form, part_form=part_form)

@service_bp.route('/edit/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    job = db.session.get(ServiceJob, job_id)
    if not job:
        flash('ไม่พบงานซ่อมที่ระบุ', 'danger')
        return redirect(url_for('service.list_jobs'))
    
    form = ServiceJobForm(obj=job)
    if form.validate_on_submit():
        job.customer_id = form.customer.data.id
        job.title = form.title.data
        job.problem_description = form.problem_description.data
        job.status = ServiceJobStatus[form.status.data]
        db.session.commit()
        flash('แก้ไขข้อมูลใบงานเรียบร้อยแล้ว', 'success')
        return redirect(url_for('service.job_detail', job_id=job.id))
        
    return render_template('service/service_form.html', title='แก้ไขใบงาน', form=form)

@service_bp.route('/task/toggle/<int:task_id>', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = db.session.get(Task, task_id)
    if task:
        task.is_completed = not task.is_completed
        db.session.commit()
    return redirect(url_for('service.job_detail', job_id=task.service_job_id))

@service_bp.route('/task/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if task:
        job_id = task.service_job_id
        db.session.delete(task)
        db.session.commit()
        flash('ลบงานย่อยเรียบร้อยแล้ว', 'success')
        return redirect(url_for('service.job_detail', job_id=job_id))
    return redirect(request.referrer or url_for('core.dashboard'))

@service_bp.route('/part/delete/<int:part_id>', methods=['POST'])
@login_required
def delete_part(part_id):
    part = db.session.get(ServiceJobPart, part_id)
    if part:
        job_id = part.service_job_id
        product = part.product
        product.stock_quantity += part.quantity
        
        db.session.delete(part)
        db.session.commit()
        flash(f'ลบรายการอะไหล่ "{product.name}" และคืนสต็อกเรียบร้อยแล้ว', 'success')
        return redirect(url_for('service.job_detail', job_id=job_id))
    return redirect(request.referrer or url_for('core.dashboard'))
