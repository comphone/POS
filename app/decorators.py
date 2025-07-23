from functools import wraps
from flask import abort
from flask_login import current_user
from .models import UserRole

def admin_required(f):
    """
    Decorator ที่ตรวจสอบว่าผู้ใช้ปัจจุบันมีบทบาทเป็น ADMIN หรือไม่
    หากไม่ใช่ จะแสดงหน้า 403 Forbidden
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

# ในอนาคต เราสามารถสร้าง decorator อื่นๆ เพิ่มเติมได้ที่นี่
# def manager_required(f):
#     ...
