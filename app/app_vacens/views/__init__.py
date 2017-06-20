from flask import Blueprint

home_vac = Blueprint('home_vac', __name__)
main_vac = Blueprint('main_vac', __name__)
admin_vac = Blueprint('admin_vac', __name__)

from . import home, main, admin