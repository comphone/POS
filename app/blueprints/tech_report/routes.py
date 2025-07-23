from flask import render_template, request
from flask_login import login_required
from . import tech_report_bp
from app.models import User, JobUpdate
from sqlalchemy import func
from app import db
from datetime import datetime

@tech_report_bp.route('/')
@login_required
def report():
    now = datetime.now()
    # รับค่าเดือนและปีจาก URL query, ถ้าไม่มีให้ใช้เดือนและปีปัจจุบัน
    year = request.args.get('year', now.year, type=int)
    month = request.args.get('month', now.month, type=int)

    # สร้าง Query เพื่อนับจำนวน JobUpdate ที่แต่ละ User สร้างในเดือนและปีที่เลือก
    report_query = db.session.query(
        User.id,
        User.first_name,
        User.last_name,
        func.count(JobUpdate.id).label('job_update_count')
    ).join(JobUpdate, User.id == JobUpdate.author_id).filter(
        func.extract('year', JobUpdate.created_at) == year,
        func.extract('month', JobUpdate.created_at) == month
    ).group_by(User.id).order_by(func.count(JobUpdate.id).desc()).all()

    # เตรียมข้อมูลสำหรับ dropdown filter
    years = range(now.year - 5, now.year + 1)
    months = [
        {'value': i, 'name': datetime(now.year, i, 1).strftime('%B')}
        for i in range(1, 13)
    ]

    return render_template('tech_report/report.html',
                           report_data=report_query,
                           selected_year=year,
                           selected_month=month,
                           years=years,
                           months=months)
