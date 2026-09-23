"""
Application Configuration
Smart Food Management System
"""

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-food-aiml-secret-key-2026')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # MySQL Database Settings (Defaults can be overridden via environment variables)
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'root')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'smart_food_management')
