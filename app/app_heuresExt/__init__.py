from flask import Blueprint

heures_ext_bp = Blueprint('heures_ext_bp', __name__)

from . import views
