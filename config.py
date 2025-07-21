import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Base configuration class.
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-super-secret-key-for-testing-only'
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'a-super-secret-csrf-key-for-testing'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # LINE Bot Configuration
    LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET') or 'YOUR_CHANNEL_SECRET'
    LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN') or 'YOUR_CHANNEL_ACCESS_TOKEN'

class DevelopmentConfig(Config):
    """
    Development configuration.
    """
    DEBUG = True
    # ในโหมด dev, ถ้าไม่มี DATABASE_URL ให้ใช้ไฟล์ app.db แทน
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')

class ProductionConfig(Config):
    """
    Production configuration.
    """
    DEBUG = False
    # สำหรับ Production, เราคาดหวังว่า DATABASE_URL จะต้องถูกตั้งค่าไว้เสมอ
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # [แก้ไข] เราจะย้ายการตรวจสอบไปไว้ใน __init__.py แทนเพื่อความยืดหยุ่น

config_by_name = dict(
    dev=DevelopmentConfig,
    prod=ProductionConfig
)
