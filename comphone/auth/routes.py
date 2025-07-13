from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
import sqlalchemy as sa
from comphone import db
from comphone.auth import bp
from comphone.auth.forms import LoginForm, RegistrationForm # ต้องแน่ใจว่ามี RegistrationForm ใน forms.py
from comphone.models import User

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    หน้า Login สำหรับผู้ใช้งาน
    Endpoint: auth.login
    """
    if current_user.is_authenticated:
        return redirect(url_for('core.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('core.index'))
    return render_template('auth/login.html', title='เข้าสู่ระบบ', form=form)

@bp.route('/logout')
def logout():
    """
    ฟังก์ชัน Logout ผู้ใช้งาน
    Endpoint: auth.logout
    """
    logout_user()
    flash('ออกจากระบบเรียบร้อยแล้ว', 'info')
    return redirect(url_for('auth.login')) # Redirect กลับไปหน้า Login หลังจาก Logout

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    หน้าลงทะเบียนผู้ใช้งานใหม่ (สำหรับ Admin หรือการตั้งค่าเริ่มต้น)
    Endpoint: auth.register
    """
    # ตรวจสอบว่าผู้ใช้ปัจจุบันเป็น admin หรือไม่ หากไม่ใช่ admin จะไม่สามารถเข้าถึงหน้า register ได้
    # หรืออาจจะอนุญาตให้ลงทะเบียนได้เฉพาะเมื่อยังไม่มีผู้ใช้ในระบบเลย (สำหรับ setup ครั้งแรก)
    # ตัวอย่างนี้จะอนุญาตให้ register ได้ถ้ายังไม่มีผู้ใช้ หรือถ้าผู้ใช้ปัจจุบันเป็น admin
    if current_user.is_authenticated and not current_user.is_admin:
        flash('คุณไม่มีสิทธิ์ลงทะเบียนผู้ใช้งานใหม่', 'danger')
        return redirect(url_for('core.index'))

    # ตรวจสอบว่ามีผู้ใช้ในระบบแล้วหรือไม่ ถ้ามีและไม่ใช่ admin จะไม่อนุญาตให้ register
    # (สามารถปรับ logic นี้ได้ตามความต้องการของระบบ)
    user_count = db.session.query(User.id).count()
    if user_count > 0 and (not current_user.is_authenticated or not current_user.is_admin):
        flash('ระบบมีการลงทะเบียนผู้ใช้งานแล้ว. หากต้องการเพิ่มผู้ใช้งาน กรุณาติดต่อผู้ดูแลระบบ.', 'warning')
        return redirect(url_for('auth.login')) # หรือหน้าที่เหมาะสม

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, is_admin=form.is_admin.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'ผู้ใช้งาน {form.username.data} ได้รับการลงทะเบียนเรียบร้อยแล้ว!', 'success')
        return redirect(url_for('auth.login')) # ลงทะเบียนเสร็จแล้วให้ไปหน้า Login
    return render_template('auth/register.html', title='ลงทะเบียนผู้ใช้งาน', form=form)

