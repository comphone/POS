from flask import render_template
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
    หน้า Dashboard หลักที่ได้รับการปรับปรุง UI/UX
    """
    jobs_query = ServiceJob.query

    # --- Logic การนับสถิติ ---
    total_jobs = jobs_query.count()
    completed_jobs = jobs_query.filter(ServiceJob.status == ServiceJobStatus.COMPLETED).count()
    
    pending_jobs = jobs_query.filter(
        ServiceJob.status.notin_([ServiceJobStatus.COMPLETED, ServiceJobStatus.CANCELLED])
    ).count()

    today_start_thai = datetime.now(THAILAND_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end_thai = today_start_thai + timedelta(days=1)
    
    today_start_utc = today_start_thai.astimezone(pytz.utc)
    today_end_utc = today_end_thai.astimezone(pytz.utc)
    
    today_jobs_count = jobs_query.filter(
        ServiceJob.due_date >= today_start_utc,
        ServiceJob.due_date < today_end_utc,
        ServiceJob.status.notin_([ServiceJobStatus.COMPLETED, ServiceJobStatus.CANCELLED])
    ).count()

    stats = {
        'total': total_jobs,
        'completed': completed_jobs,
        'pending': pending_jobs,
        'today': today_jobs_count
    }

    recent_jobs = jobs_query.order_by(ServiceJob.created_at.desc()).limit(10).all()

    return render_template('core/dashboard.html', stats=stats, recent_jobs=recent_jobs)
