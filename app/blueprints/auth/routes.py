from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from .forms import LoginForm
from . import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('core.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        # ค้นหา user จาก email ที่กรอกเข้ามา
        user = User.query.filter_by(email=form.email.data).first()
        
        # ตรวจสอบว่า user มีอยู่จริงและรหัสผ่านถูกต้องหรือไม่
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            
            next_page = request.args.get('next')
            flash('เข้าสู่ระบบสำเร็จ!', 'success')
            return redirect(next_page or url_for('core.dashboard'))
        else:
            flash('อีเมลหรือรหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('คุณออกจากระบบเรียบร้อยแล้ว', 'info')
    return redirect(url_for('auth.login'))

# เราจะทำหน้า Register ใน Session ถัดๆ ไป
@auth_bp.route('/register')
def register():
    return "Register page is under construction."
