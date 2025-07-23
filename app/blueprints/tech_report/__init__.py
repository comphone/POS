# ===================================================================
# File: app/blueprints/tech_report/__init__.py (สร้างไฟล์ใหม่)
# ===================================================================
from flask import Blueprint

tech_report_bp = Blueprint(
    'tech_report', __name__,
    template_folder='templates'
)

from . import routes


# ===================================================================
# File: app/blueprints/tech_report/routes.py (สร้างไฟล์ใหม่)
# ===================================================================
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

# ===================================================================
# File: app/blueprints/tech_report/templates/tech_report/report.html (สร้างไฟล์ใหม่)
# ===================================================================
{% extends "base.html" %}

{% block title %}รายงานช่าง{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center pt-3 pb-2 mb-3 border-bottom">
    <h1 class="h2"><i class="fas fa-user-chart me-2"></i>รายงานสรุปการทำงานของช่าง</h1>
</div>

<div class="card shadow-sm mb-4">
    <div class="card-body">
        <form method="GET" class="row g-3 align-items-center">
            <div class="col-auto">
                <label for="month" class="form-label">เดือน:</label>
                <select name="month" id="month" class="form-select">
                    {% for m in months %}
                    <option value="{{ m.value }}" {% if m.value == selected_month %}selected{% endif %}>{{ m.name }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-auto">
                <label for="year" class="form-label">ปี:</label>
                <select name="year" id="year" class="form-select">
                    {% for y in years %}
                    <option value="{{ y }}" {% if y == selected_year %}selected{% endif %}>{{ y }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-auto mt-auto">
                <button type="submit" class="btn btn-primary">ดูรายงาน</button>
            </div>
        </form>
    </div>
</div>


<div class="card shadow-sm">
    <div class="card-header">
        <h5 class="mb-0">สรุปจำนวนการลงรายงานประจำเดือน {{ selected_month }}/{{ selected_year }}</h5>
    </div>
    <div class="card-body">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>#</th>
                    <th>ชื่อช่าง</th>
                    <th class="text-center">จำนวนการลงรายงาน</th>
                </tr>
            </thead>
            <tbody>
                {% for tech in report_data %}
                <tr>
                    <td>{{ loop.index }}</td>
                    <td>{{ tech.first_name }} {{ tech.last_name }}</td>
                    <td class="text-center">{{ tech.job_update_count }}</td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="3" class="text-center">ไม่พบข้อมูลในเดือนที่เลือก</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
