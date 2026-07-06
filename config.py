import os

class Config:
    # Flask Session & CSRF Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'anti-gravity-magnetic-flux-shield-key-9821'
    
    # Database Configuration
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'site.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Upload Settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'jpg', 'jpeg', 'png'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB maximum upload limit
    
    # Auto-delete configuration (files older than this will be deleted)
    FILE_RETENTION_HOURS = 2
