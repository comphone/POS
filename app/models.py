"""
Comphone Integrated System - Unified Database Models (Feature Set 1 Update)
- Added SystemSettings model to replace settings.json
"""

from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import json
import enum

# --- Enums for consistent choices ---
class UserRole(enum.Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    TECHNICIAN = 'technician'
    SALES = 'sales'
    SUPPORT = 'support'

class ServiceJobStatus(enum.Enum):
    RECEIVED = 'received'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

# ... (Enums อื่นๆ ที่มีอยู่แล้ว) ...

# --- Association Tables ---
task_assignees = db.Table('task_assignees',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# --- Main Models ---

class User(UserMixin, db.Model):
    # ... (โค้ด User Model เหมือนเดิมทุกประการ) ...
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.TECHNICIAN, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Customer(db.Model):
    # ... (โค้ด Customer Model เหมือนเดิมทุกประการ) ...
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    phone = db.Column(db.String(20), index=True)
    address = db.Column(db.Text)

# ... (Models อื่นๆ เช่น ServiceJob, Product, Sale, Task ฯลฯ เหมือนเดิม) ...

# [เพิ่ม] Model สำหรับเก็บการตั้งค่าระบบทั้งหมด
class SystemSettings(db.Model):
    """System settings and configuration, replacing settings.json."""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    category = db.Column(db.String(50), default='general', index=True)
    
    def __repr__(self):
        return f'<Setting {self.key}>'

