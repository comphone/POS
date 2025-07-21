# ===================================================================
# File: app/blueprints/accounting/__init__.py
# ===================================================================
from flask import Blueprint

accounting_bp = Blueprint(
    'accounting', __name__,
    template_folder='templates'
)

from . import routes