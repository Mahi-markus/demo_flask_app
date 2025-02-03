import unittest
from server import create_app, db ,Message


class MessageApiTestCase(unittest.TestCase):
    """Unit tests for the Flask API"""

    @classmethod
    def setUpClass(cls):
        """Set up the test environment before tests run"""
        cls.app = create_app()  # Use the create_app function to get the app
        cls.client = cls.app.test_client()  # Test client for simulating requests
        
        # Set the database URI to an in-memory SQLite database for testing
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.app.config['TESTING'] = True

    def setUp(self):
        """Set up before each test (database migration, etc.)"""
        with self.app.app_context():
            db.create_all()  # Create all tables (in-memory database)

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()  # Remove the session
            db.drop_all()  # Drop all tables

    def test_get_message_no_data(self):
        """Test GET /api/message when no messages exist"""
        response = self.client.get('/api/message')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['messages'], [])  # No messages should be returned

    def test_post_message_success(self):
        """Test POST /api/message with valid data"""
        response = self.client.post('/api/message', json={'content': 'Hello, world!'})
        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Message created successfully')
        self.assertEqual(data['data']['content'], 'Hello, world!')

    def test_post_message_missing_content(self):
        """Test POST /api/message when content is missing"""
        response = self.client.post('/api/message', json={})
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Content is required')

    def test_post_message_no_data(self):
        """Test POST /api/message with no data"""
        response = self.client.post('/api/message', data=None)  # No JSON body
        data = response.get_json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'No data provided')

    def test_get_message_with_data(self):
        """Test GET /api/message when there are messages"""
        # Add a message to the database
        message = Message(content="Test message")
        with self.app.app_context():
            db.session.add(message)
            db.session.commit()

        # Fetch the messages
        response = self.client.get('/api/message')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['messages']), 1)
        self.assertEqual(data['messages'][0]['content'], 'Test message')

if __name__ == '__main__':
    unittest.main()
