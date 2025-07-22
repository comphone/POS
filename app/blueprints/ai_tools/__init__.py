from flask import Blueprint

# 1. สร้าง Blueprint object ก่อน
ai_tools_bp = Blueprint(
    'ai_tools', __name__,
    template_folder='templates'
)

# 2. Import routes ในบรรทัดสุดท้ายเสมอ
from . import routes
