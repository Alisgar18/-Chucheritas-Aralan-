import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'centerbeam.proxy.rlwy.net')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'APP_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '4l1Sl4m4s')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'CHUCHERITAS_ARALAN')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    
    # Flask
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'Th4s_Th4t_m3_3Spr3ss0')