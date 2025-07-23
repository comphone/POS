# ===================================================================
# File: app/__init__.py (ฉบับเต็ม)
# ===================================================================
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, timezone

from config import config_by_name

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'กรุณาเข้าสู่ระบบเพื่อเข้าถึงหน้านี้'
login_manager.login_message_category = 'info'


def create_app(config_name='dev'):
    app = Flask(__name__)
    config_obj = config_by_name[config_name]
    app.config.from_object(config_obj)

    # ... (init_app calls) ...
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from . import models

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(models.User, int(user_id))

    @app.context_processor
    def inject_global_vars():
        return dict(current_year=datetime.now(timezone.utc).year)

    # --- Register Blueprints ---
    from .blueprints.core import core_bp
    app.register_blueprint(core_bp)
    from .blueprints.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from .blueprints.customer import customer_bp
    app.register_blueprint(customer_bp, url_prefix='/customer')
    from .blueprints.inventory import inventory_bp
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    from .blueprints.service import service_bp
    app.register_blueprint(service_bp, url_prefix='/service')
    from .blueprints.pos import pos_bp
    app.register_blueprint(pos_bp, url_prefix='/pos')
    from .blueprints.accounting import accounting_bp
    app.register_blueprint(accounting_bp, url_prefix='/accounting')
    
    # [เพิ่ม] ลงทะเบียน Settings Blueprint
    from .blueprints.settings import settings_bp
    app.register_blueprint(settings_bp, url_prefix='/settings')


    with app.app_context():
        db.create_all()
        # Optional: Add code here to populate default settings if the table is empty
        if not models.SystemSettings.query.first():
            print("Populating default system settings...")
            default_settings = [
                models.SystemSettings(key='line_admin_group_id', value='', description='LINE Admin Group ID', category='line_bot'),
                models.SystemSettings(key='appointment_reminder_hour', value='7', description='เวลาแจ้งเตือนนัดหมาย (โมง)', category='notifications'),
                # Add more default settings here
            ]
            db.session.bulk_save_objects(default_settings)
            db.session.commit()

        if not models.User.query.filter_by(email='admin@example.com').first():
            # ... (code to create default admin user) ...
            pass

    return app