from flask import Blueprint

vac_ens_bp = Blueprint('vac_ens_bp', __name__)

from . import views