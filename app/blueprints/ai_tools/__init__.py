# ===================================================================
# File: app/blueprints/ai_tools/__init__.py (สร้างไฟล์ใหม่)
# ===================================================================
from flask import Blueprint

ai_tools_bp = Blueprint(
    'ai_tools', __name__,
    template_folder='templates'
)

from . import routes


# ===================================================================
# File: app/blueprints/ai_tools/routes.py (สร้างไฟล์ใหม่)
# ===================================================================
from flask import jsonify
from flask_login import login_required
from . import ai_tools_bp
from app import db
from app.models import ServiceJob

@ai_tools_bp.route('/get_job_history/<int:job_id>')
@login_required
def get_job_history(job_id):
    """
    API Endpoint ที่ส่งคืนประวัติการอัปเดตทั้งหมดของงานซ่อม
    ในรูปแบบ JSON เพื่อให้ JavaScript นำไปใช้ต่อ
    """
    job = db.session.get(ServiceJob, job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    # รวบรวมประวัติทั้งหมด
    history = []
    for update in job.updates:
        history.append(
            f"- {update.created_at.strftime('%d/%m/%Y %H:%M')} "
            f"โดย {update.author.full_name}: {update.summary}"
        )
    
    # เรียงลำดับจากเก่าไปใหม่เพื่อให้ AI อ่านง่าย
    history.reverse()
    
    history_text = "\n".join(history)
    
    return jsonify({
        "job_title": job.title,
        "problem_description": job.problem_description,
        "history": history_text
    })
