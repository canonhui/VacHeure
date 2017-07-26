from flask import Blueprint

cons_ens_bp = Blueprint('cons_ens_bp', __name__)

from . import views