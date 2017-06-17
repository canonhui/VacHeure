from flask import Blueprint

home_bp = Blueprint('home_bp', __name__)
main_bp = Blueprint('main_bp', __name__)
admin_bp = Blueprint('admin_bp', __name__)

from . import home, main, admin