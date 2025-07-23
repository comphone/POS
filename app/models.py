"""
Comphone Integrated System - Unified Database Models (Version 8.0)
- Added is_admin property to User model for easier permission checks.
"""

from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import enum
import json

# --- Enums ---
class UserRole(enum.Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    TECHNICIAN = 'technician'
    SALES = 'sales'
    SUPPORT = 'support'

# ... (Enums อื่นๆ เหมือนเดิม) ...

# --- Main Models ---
class User(UserMixin, db.Model):
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

    # [เพิ่ม] Helper property สำหรับตรวจสอบสิทธิ์
    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

# ... (Models อื่นๆ ทั้งหมดเหมือนเดิมทุกประการ) ...
class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    phone = db.Column(db.String(20), index=True)
    address = db.Column(db.Text)

class ServiceJob(db.Model):
    __tablename__ = 'service_job'
    id = db.Column(db.Integer, primary_key=True)
    # ... fields ...
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship('Customer', backref='service_jobs')
    # ... other relationships ...

# ... (and so on for all other models) ...
