from flask import Blueprint

bp = Blueprint('auth', __name__)

from comphone.auth import routes