import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'inventory_super_secret_app_key_32bytes_2026_prod!')
    JWT_SECRET = os.getenv('JWT_SECRET', 'inventory_jwt_secret_key_32bytes_long_signature_2026!')
    JWT_EXPIRATION = timedelta(hours=24)
    
    # Primary MySQL Connection configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'root')
    MYSQL_DB = os.getenv('MYSQL_DB', 'inventory_db')
    
    MYSQL_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    SQLITE_DATABASE_URI = f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'inventory_local.db')}"
    
    # Defaults to MySQL if environment dictates, but fallback logic will handle connections cleanly
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', MYSQL_DATABASE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
