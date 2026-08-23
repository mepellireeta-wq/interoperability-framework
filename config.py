import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Central Configuration for Universal Government Interoperability Middleware"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'universal-gov-interop-secret-key-2026-secure')
    
    # SQLite Database URI
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        f'sqlite:///{os.path.join(BASE_DIR, "database", "interop.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SSO & JWT Authentication Settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'sso-federated-jwt-secret-2026')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    
    # Master Data Management (MDM) & Data Quality Thresholds
    STATE_ID_SALT = os.getenv('STATE_ID_SALT', 'universal-state-citizen-salt')
    SLA_WARNING_HOURS = 48
    SLA_CRITICAL_HOURS = 96
    
    # Department Endpoint Configurations (Simulated API Ports)
    DEPT_A_SKILLS_URL = os.getenv('DEPT_A_URL', 'http://127.0.0.1:5001/api/skills')
    DEPT_B_EMPLOYMENT_URL = os.getenv('DEPT_B_URL', 'http://127.0.0.1:5002/api/employment')
    DEPT_C_ENTREPRENEURSHIP_URL = os.getenv('DEPT_C_URL', 'http://127.0.0.1:5003/api/entrepreneurship')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config_by_name = {
    'dev': DevelopmentConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
