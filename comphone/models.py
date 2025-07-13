# comphone_pos/comphone/models.py (ฉบับอัปเดตสำหรับแก้ไข Eager Loading - v2)

from datetime import datetime, timezone
from typing import Optional, List
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from comphone import db, login

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    is_admin: so.Mapped[bool] = so.mapped_column(default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if self.password_hash is None: return False
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

class Customer(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(150), index=True)
    phone: so.Mapped[Optional[str]] = so.mapped_column(sa.String(50))
    address: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
    service_jobs: so.WriteOnlyMapped['ServiceJob'] = so.relationship(back_populates='customer')
    sales: so.WriteOnlyMapped['Sale'] = so.relationship(back_populates='customer')


class Product(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(150), index=True, unique=True)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
    cost_price: so.Mapped[float] = so.mapped_column(sa.Float, default=0.0)
    selling_price: so.Mapped[float] = so.mapped_column(sa.Float, default=0.0)
    quantity: so.Mapped[int] = so.mapped_column(default=0)

class StockMovement(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    product_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('product.id'), index=True)
    change: so.Mapped[int]
    reason: so.Mapped[str] = so.mapped_column(sa.String(50))
    timestamp: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    related_id: so.Mapped[Optional[int]] = so.mapped_column()

class Sale(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    timestamp: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    total_amount: so.Mapped[float] = so.mapped_column(sa.Float)
    customer_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('customer.id'))
    # แก้ไขตรงนี้: เพิ่ม lazy='joined' หรือ lazy='selectin'
    items: so.Mapped[List['SaleItem']] = so.relationship(back_populates='sale', cascade="all, delete-orphan", lazy='selectin')
    customer: so.Mapped[Optional['Customer']] = so.relationship(back_populates='sales')


class SaleItem(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    sale_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('sale.id'), index=True)
    product_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('product.id'), index=True)
    quantity: so.Mapped[int]
    price_per_item: so.Mapped[float] = so.mapped_column(sa.Float)
    sale: so.Mapped[Sale] = so.relationship(back_populates='items')
    product: so.Mapped[Product] = so.relationship()

# --- ส่วนที่เพิ่มสำหรับระบบงานซ่อม ---
class ServiceJob(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    customer_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('customer.id'), index=True)
    description: so.Mapped[str] = so.mapped_column(sa.String(500))
    status: so.Mapped[str] = so.mapped_column(sa.String(50), default='รอดำเนินการ')
    created_at: so.Mapped[datetime] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    
    customer: so.Mapped[Customer] = so.relationship(back_populates='service_jobs')
    parts_used: so.Mapped[List['ServicePartUsage']] = so.relationship(back_populates='service_job', cascade="all, delete-orphan")

class ServicePartUsage(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    service_job_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('service_job.id'), index=True)
    product_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('product.id'), index=True)
    quantity_used: so.Mapped[int]
    
    service_job: so.Mapped[ServiceJob] = so.relationship(back_populates='parts_used')
    product: so.Mapped[Product] = so.relationship()
