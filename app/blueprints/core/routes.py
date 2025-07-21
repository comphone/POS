from flask import render_template
from flask_login import login_required, current_user
from . import core_bp

@core_bp.route('/')
@core_bp.route('/dashboard')
@login_required
def dashboard():
    """
    หน้า Dashboard หลักหลังจาก Login
    """
    return render_template('core/dashboard.html')
