from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Establish relationship to conversion history records
    conversions = db.relationship('ConversionHistory', backref='user', lazy=True, cascade="all, delete-orphan")

    def __init__(self, username, email, password_hash):
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def __repr__(self):
        return f"<User {self.username}>"

class ConversionHistory(db.Model):
    __tablename__ = 'conversion_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    converted_filename = db.Column(db.String(255), nullable=False)
    conversion_type = db.Column(db.String(50), nullable=False)  # 'pdf_to_docx' or 'docx_to_pdf'
    status = db.Column(db.String(50), default='success')        # 'success', 'failed', 'processing'
    file_size = db.Column(db.String(50), nullable=True)          # Friendly file size, e.g. "1.4 MB"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id, original_filename, converted_filename, conversion_type, status='success', file_size=None):
        self.user_id = user_id
        self.original_filename = original_filename
        self.converted_filename = converted_filename
        self.conversion_type = conversion_type
        self.status = status
        self.file_size = file_size

    def __repr__(self):
        return f"<ConversionHistory {self.conversion_type}: {self.original_filename} -> {self.converted_filename}>"
