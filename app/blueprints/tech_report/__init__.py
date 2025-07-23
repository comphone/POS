from flask import Blueprint

tech_report_bp = Blueprint(
    'tech_report', __name__,
    template_folder='templates'
)

from . import routes
