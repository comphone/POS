# โค้ดที่ถูกต้องจาก Canvas
from flask import Blueprint

service_bp = Blueprint(
    'service', __name__,
    template_folder='templates',
    static_folder='static'
)

from . import routes