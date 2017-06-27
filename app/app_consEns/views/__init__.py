from flask import Blueprint

home_cons_bp = Blueprint('home_cons_bp', __name__)
main_cons_bp = Blueprint('main_cons_bp', __name__)
admin_cons_bp = Blueprint('admin_cons_bp', __name__)

from . import home, main, admin