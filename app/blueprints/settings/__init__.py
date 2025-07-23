# ===================================================================
# File: app/blueprints/settings/__init__.py (สร้างไฟล์ใหม่)
# ===================================================================
from flask import Blueprint

settings_bp = Blueprint(
    'settings', __name__,
    template_folder='templates'
)

from . import routes


# ===================================================================
# File: app/blueprints/settings/routes.py (สร้างไฟล์ใหม่)
# ===================================================================
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from . import settings_bp
from app import db
from app.models import SystemSettings

@settings_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        # Loop through form data and update settings in the database
        for key, value in request.form.items():
            setting = SystemSettings.query.filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                # Optional: create setting if it doesn't exist
                new_setting = SystemSettings(key=key, value=value)
                db.session.add(new_setting)
        
        db.session.commit()
        flash('บันทึกการตั้งค่าเรียบร้อยแล้ว!', 'success')
        return redirect(url_for('settings.index'))

    # Query all settings from the database and group them by category
    settings_query = SystemSettings.query.order_by(SystemSettings.category).all()
    settings_by_category = {}
    for s in settings_query:
        if s.category not in settings_by_category:
            settings_by_category[s.category] = []
        settings_by_category[s.category].append(s)
        
    return render_template('settings/settings.html', settings_by_category=settings_by_category)


# ===================================================================
# File: app/blueprints/settings/templates/settings/settings.html (สร้างไฟล์ใหม่)
# ===================================================================
{% extends "base.html" %}

{% block title %}ตั้งค่าระบบ{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h1 class="h2 mb-0">⚙️ ตั้งค่าระบบ</h1>
</div>

<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>

    {% for category, settings in settings_by_category.items() %}
    <div class.card shadow-sm mb-4>
        <div class="card-header bg-light">
            <h5 class="mb-0 text-capitalize">{{ category.replace('_', ' ') }}</h5>
        </div>
        <div class="card-body p-4">
            {% for setting in settings %}
            <div class="row mb-3">
                <label for="{{ setting.key }}" class="col-md-4 col-form-label">{{ setting.description or setting.key }}</label>
                <div class="col-md-8">
                    <input type="text" class="form-control" id="{{ setting.key }}" name="{{ setting.key }}"
                           value="{{ setting.value or '' }}">
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endfor %}

    <div class="text-center mb-5">
        <button type="submit" class="btn btn-success btn-lg">
            <i class="fas fa-save me-2"></i>บันทึกการตั้งค่าทั้งหมด
        </button>
    </div>
</form>
{% endblock %}
