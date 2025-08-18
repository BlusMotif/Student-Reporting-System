import unittest
from app import app

class ForgotPasswordTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_forgot_password(self):
        response = self.app.post('/forgot_password', data={
            'email': 'test@example.com',
            'reset_method': 'email',
            'student_id': '123456'
        })
        self.assertEqual(response.status_code, 302)  # Check for redirect after form submission
        self.assertIn(b'Reset link has been sent!', response.data)  # Check for success message

if __name__ == '__main__':
    unittest.main()
