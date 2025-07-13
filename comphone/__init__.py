# comphone/__init__.py (ฉบับปรับปรุง)
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from sqlalchemy import MetaData

# กำหนด convention สำหรับชื่อคีย์ในฐานข้อมูล (ช่วยในการจัดการ migration)
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

db = SQLAlchemy(metadata=MetaData(naming_convention=convention))
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login' # กำหนดหน้า Login ที่จะถูก redirect ไปเมื่อเข้าถึงหน้าที่ต้องล็อกอิน
login.login_message = 'กรุณาเข้าสู่ระบบเพื่อใช้งานหน้านี้'
login.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    # render_as_batch=True จำเป็นสำหรับ SQLite เพื่อรองรับการเปลี่ยนชื่อคอลัมน์ใน migration
    migrate.init_app(app, db, render_as_batch=True)
    login.init_app(app)

    # --- ลงทะเบียน Blueprints ทั้งหมด ---
    # Blueprint สำหรับการยืนยันตัวตน (Login, Logout, Register)
    from comphone.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Blueprint สำหรับฟังก์ชันหลักของระบบ (Dashboard, Customer Management)
    from comphone.core.routes import bp as core_bp
    app.register_blueprint(core_bp) # ไม่ต้องมี url_prefix เพราะเป็น Blueprint หลัก

    # Blueprint สำหรับการจัดการคลังสินค้า
    from comphone.inventory.routes import bp as inventory_bp
    app.register_blueprint(inventory_bp, url_prefix='/inventory')

    # Blueprint สำหรับหน้าขาย (Point of Sale)
    from comphone.pos.routes import bp as pos_bp
    app.register_blueprint(pos_bp, url_prefix='/pos')

    # Blueprint สำหรับระบบงานซ่อม
    from comphone.service.routes import bp as service_bp
    app.register_blueprint(service_bp, url_prefix='/service')

    # Blueprint สำหรับบัญชีและรายงาน (เพิ่มใหม่)
    from comphone.accounting.routes import bp as accounting_bp
    app.register_blueprint(accounting_bp, url_prefix='/accounting')

    return app

