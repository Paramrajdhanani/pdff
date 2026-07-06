import sys
import os
import unittest

# Adjust path if needed
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from models import db, User, ConversionHistory
from config import Config

class TestAppConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing forms simply

class ConverterProVerification(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestAppConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        db.session.remove()
        self.app_context.pop()

    def test_database_creation(self):
        """Verifies database tables are created correctly."""
        # Querying db tables to assert existence
        users = User.query.all()
        history = ConversionHistory.query.all()
        self.assertEqual(len(users), 0)
        self.assertEqual(len(history), 0)

    def test_routes_exist_guest(self):
        """Verifies public routes render or redirect correctly for guests."""
        # Home landing
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Transpose Streams', response.data)

        # Login page
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ACCESS PORTAL', response.data)

        # Signup page
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'INITIALIZE IDENTITY', response.data)

    def test_protected_routes_redirect_guest(self):
        """Verifies that accessing protected routes as guest redirects to login."""
        protected_routes = ['/dashboard', '/converter', '/history', '/success/1', '/download/test.pdf']
        for route in protected_routes:
            response = self.client.get(route)
            # Should be redirecting (302) to login screen
            self.assertEqual(response.status_code, 302, f"Route {route} did not redirect guest.")

    def test_convert_invalid_type_guest(self):
        """Verifies convert endpoint redirects guest even with data."""
        response = self.client.post('/convert', data={'conversion_type': 'merge_pdf'})
        self.assertEqual(response.status_code, 302)

if __name__ == '__main__':
    unittest.main()
