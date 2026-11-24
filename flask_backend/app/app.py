import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 从 flask_backend/.env 读取密钥与数据库配置（.env 不纳入版本控制）
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))
except ImportError:
    pass

from flask import Flask
from app.models.base import db
from flask_redis import FlaskRedis
from flask_cors import CORS

redis_client = FlaskRedis()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        force=True
    )

    class Config:
        """基础配置类"""
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'

        SQLALCHEMY_TRACK_MODIFICATIONS = False

        REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6377/0'

    class DevelopmentConfig(Config):
        """开发环境配置"""
        DEBUG = True
        SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')

    class TestingConfig(Config):
        """测试环境配置"""
        TESTING = True
        SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')

    class ProductionConfig(Config):
        """生产环境配置"""
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    config = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig,
        'default': DevelopmentConfig
    }
    
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    app.config.from_object(config[config_name])

    db.init_app(app)
    redis_client.init_app(app)
    CORS(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp)

    with app.app_context():
        from app.models import TourismResource, AdministrativeDivision, EvaluationFactor, User
    
    return app