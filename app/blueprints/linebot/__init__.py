# ===================================================================
# File: app/blueprints/linebot/__init__.py
# ===================================================================
from flask import Blueprint

linebot_bp = Blueprint('linebot', __name__)

from . import routes