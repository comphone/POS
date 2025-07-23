from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from . import settings_bp
from app import db
from app.models import SystemSettings
from app.decorators import admin_required

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def index():
    if request.method == 'POST':
        for key, value in request.form.items():
            setting = SystemSettings.query.filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                new_setting = SystemSettings(key=key, value=value)
                db.session.add(new_setting)
        
        db.session.commit()
        flash('บันทึกการตั้งค่าเรียบร้อยแล้ว!', 'success')
        return redirect(url_for('settings.index'))

    settings_query = SystemSettings.query.order_by(SystemSettings.category).all()
    settings_by_category = {}
    for s in settings_query:
        if s.category not in settings_by_category:
            settings_by_category[s.category] = []
        settings_by_category[s.category].append(s)
        
    return render_template('settings/settings.html', settings_by_category=settings_by_category)
