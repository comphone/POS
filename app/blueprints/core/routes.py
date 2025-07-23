from flask import render_template, request
from flask_login import login_required
from . import core_bp
from app.models import ServiceJob, ServiceJobStatus
from datetime import datetime, timedelta
import pytz

THAILAND_TZ = pytz.timezone('Asia/Bangkok')

@core_bp.route('/')
@core_bp.route('/dashboard')
@login_required
def dashboard():
    """
    หน้า Dashboard หลักที่ได้รับการปรับปรุง
    """
    jobs_query = ServiceJob.query

    # Logic การนับสถิติ
    total_jobs = jobs_query.count()
    completed_jobs = jobs_query.filter(ServiceJob.status == ServiceJobStatus.COMPLETED).count()
    pending_jobs = total_jobs - completed_jobs
    
    today_start = datetime.now(THAILAND_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    today_jobs = jobs_query.filter(
        ServiceJob.due_date >= today_start.astimezone(pytz.utc),
        ServiceJob.due_date < today_end.astimezone(pytz.utc),
        ServiceJob.status != ServiceJobStatus.COMPLETED
    ).count()

    stats = {
        'total': total_jobs,
        'completed': completed_jobs,
        'pending': pending_jobs,
        'today': today_jobs
    }

    # ดึงงานล่าสุด 10 รายการมาแสดง
    recent_jobs = jobs_query.order_by(ServiceJob.created_at.desc()).limit(10).all()

    return render_template('core/dashboard.html', stats=stats, recent_jobs=recent_jobs)
