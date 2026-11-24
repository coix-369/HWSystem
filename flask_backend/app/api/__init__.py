from flask import Blueprint

bp = Blueprint('api', __name__, url_prefix='/api')

from . import routes

def init_app(app):
    """初始化API模块"""
    app.register_blueprint(bp)