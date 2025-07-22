import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    คลาส Configuration พื้นฐาน
    """
    # ดึงค่า Secret Key จาก Environment Variable เสมอ
    # หากไม่พบ จะใช้ค่า default สำหรับการพัฒนาเท่านั้น
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-default-secret-key-for-dev'
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'a-default-csrf-key-for-dev'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # การตั้งค่า LINE Bot
    LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
    LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')

class DevelopmentConfig(Config):
    """
    การตั้งค่าสำหรับโหมดพัฒนา (Development)
    """
    DEBUG = True
    # ในโหมด dev, ถ้าไม่มี DATABASE_URL ใน .env ให้ใช้ไฟล์ app.db แทน
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')

class ProductionConfig(Config):
    """
    การตั้งค่าสำหรับโหมดใช้งานจริง (Production)
    """
    DEBUG = False
    # สำหรับ Production, เราคาดหวังว่า DATABASE_URL จะต้องถูกตั้งค่าไว้ใน Environment Variable เสมอ
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

config_by_name = dict(
    dev=DevelopmentConfig,
    prod=ProductionConfig
)
