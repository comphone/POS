from flask import Blueprint

# 1. สร้าง Blueprint object ก่อน
auth_bp = Blueprint(
    'auth', __name__,
    template_folder='templates',
    static_folder='static'
)

# 2. Import routes ในบรรทัดสุดท้ายเสมอ
from . import routes
