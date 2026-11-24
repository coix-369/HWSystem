import os

# 从同目录 .env 读取密钥与数据库配置（.env 不纳入版本控制）
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
except ImportError:
    pass


class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Ensure JSON responses use UTF-8 encoding instead of ASCII escape sequences
    JSON_AS_ASCII = False

    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6377/0'

    # 豆包 AI 配置（从环境变量读取，真实值放在不纳入版本控制的 .env 中）
    DOUBAO_API_KEY = os.environ.get('DOUBAO_API_KEY')
    DOUBAO_ENDPOINT_ID = os.environ.get('DOUBAO_ENDPOINT_ID')

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