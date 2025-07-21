"""
Comphone Integrated System - Unified Database Models (Version 7.0)
- Re-added the 'address' field to the Customer model to fix migration TypeError.
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

class ServiceJobStatus(enum.Enum):
    RECEIVED = 'received'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class PaymentStatus(enum.Enum):
    PENDING = 'pending'
    PAID = 'paid'

class JobUpdateType(enum.Enum):
    REPORT = 'report'
    NOTE = 'note'

# --- Association Tables ---
task_assignees = db.Table('task_assignees',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

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

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    phone = db.Column(db.String(20), index=True)
    # [แก้ไข] เพิ่มฟิลด์ address กลับเข้ามา
    address = db.Column(db.Text)

class ServiceJob(db.Model):
    __tablename__ = 'service_job'
    id = db.Column(db.Integer, primary_key=True)
    job_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    problem_description = db.Column(db.Text)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    status = db.Column(db.Enum(ServiceJobStatus), default=ServiceJobStatus.RECEIVED, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    customer = db.relationship('Customer', backref='service_jobs')
    tasks = db.relationship('Task', backref='service_job', lazy='dynamic', cascade='all, delete-orphan')
    updates = db.relationship('JobUpdate', backref='service_job', lazy='dynamic', cascade='all, delete-orphan', order_by='JobUpdate.created_at.desc()')
    parts_used = db.relationship('ServiceJobPart', backref='service_job', lazy='dynamic', cascade='all, delete-orphan')

class JobUpdate(db.Model):
    __tablename__ = 'job_update'
    id = db.Column(db.Integer, primary_key=True)
    service_job_id = db.Column(db.Integer, db.ForeignKey('service_job.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    author = db.relationship('User', backref='job_updates')

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    service_job_id = db.Column(db.Integer, db.ForeignKey('service_job.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    assignees = db.relationship('User', secondary=task_assignees, backref=db.backref('tasks', lazy='dynamic'))

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    sku = db.Column(db.String(50), unique=True, index=True)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)

class ServiceJobPart(db.Model):
    __tablename__ = 'service_job_part'
    id = db.Column(db.Integer, primary_key=True)
    service_job_id = db.Column(db.Integer, db.ForeignKey('service_job.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_time = db.Column(db.Float, nullable=False)
    added_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    product = db.relationship('Product')
    adder = db.relationship('User')

class Sale(db.Model):
    __tablename__ = 'sale'
    id = db.Column(db.Integer, primary_key=True)
    sale_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    salesperson_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PAID)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    customer = db.relationship('Customer', backref='sales')
    salesperson = db.relationship('User', backref='sales')
    items = db.relationship('SaleItem', backref='sale', lazy='dynamic', cascade='all, delete-orphan')

class SaleItem(db.Model):
    __tablename__ = 'sale_item'
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)

    product = db.relationship('Product')
