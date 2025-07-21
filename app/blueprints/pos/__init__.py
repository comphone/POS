# ===================================================================
# File: app/blueprints/pos/__init__.py
# ===================================================================
from flask import Blueprint

pos_bp = Blueprint(
    'pos', __name__,
    template_folder='templates'
)

from . import routes