import os
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from config import Config
from models import db, User

# Initialize global Flask extensions
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = "Please sign in to access the Converter Pro terminal coordinates."
login_manager.login_message_category = "danger"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app instance
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register Blueprints
    from auth.routes import auth_bp
    from converter.routes import converter_bp

    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(converter_bp, url_prefix='/')

    # Create directories and SQLite tables
    with app.app_context():
        # Ensure instance directory exists
        instance_dir = os.path.join(app.root_path, 'instance')
        os.makedirs(instance_dir, exist_ok=True)
        
        # Ensure upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Create database tables
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    
    # Check if running in production mode via environment variable
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        try:
            from waitress import serve
            print("Launching production WSGI server (Waitress) on http://127.0.0.1:5000")
            serve(app, host='127.0.0.1', port=5000)
        except ImportError:
            print("Waitress not installed. Running Flask server in production mode (debug=False)...")
            print("To use the production WSGI server, please run: pip install waitress")
            app.run(debug=False, port=5000)
    else:
        print("Launching PDF -> Word Converter Pro on http://127.0.0.1:5000")
        app.run(debug=True, port=5000)
