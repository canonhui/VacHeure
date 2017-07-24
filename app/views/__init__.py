from flask import Blueprint

main_app_bp = Blueprint('main_app_bp', __name__)
valid_email_bp = Blueprint('valid_email_bp', __name__)

from . import main, valid_email