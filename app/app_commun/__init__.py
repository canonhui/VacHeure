from flask import Blueprint

commun_bp = Blueprint('commun_bp', __name__)

from . import views