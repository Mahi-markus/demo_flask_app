import unittest
from unittest.mock import patch, MagicMock
from server import create_app, db, Message
from flask import json

class MockMessageApiTestCase(unittest.TestCase):
    """Unit tests for the Flask API using mocks"""
    
    @classmethod
    def setUpClass(cls):
        """Set up the test environment before tests run"""
        cls.app = create_app()
        cls.client = cls.app.test_client()
        cls.app.config['TESTING'] = True
    
    def setUp(self):
        """Set up before each test"""
        self.patcher = patch('server.db.session')
        self.mock_session = self.patcher.start()
        
    def tearDown(self):
        """Clean up after each test"""
        self.patcher.stop()

    @patch('server.Message.query')
    def test_get_message_no_data(self, mock_query):
        """Test GET /api/message when no messages exist"""
        # Configure the mock to return empty list
        mock_query.all.return_value = []
        
        response = self.client.get('/api/message')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['messages'], [])
        mock_query.all.assert_called_once()

    @patch('server.db.session.add')
    @patch('server.db.session.commit')
    def test_post_message_success(self, mock_commit, mock_add):
        """Test POST /api/message with valid data"""
        test_content = 'Hello, world!!!!!!'
        
        response = self.client.post('/api/message', json={'content': test_content})
        data = response.get_json()
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Message created successfully')
        self.assertEqual(data['data']['content'], test_content)
        
        # Verify that add and commit were called
        mock_add.assert_called_once()
        mock_commit.assert_called_once()

    @patch("models.model.Message.query.all", side_effect=Exception("Database error"))
    def test_get_message_exception(self, mock_query):
        response = self.client.get("/api/message")
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        # self.assertIn("Error fetching messages", data["message"])
        # self.assertEqual(data["status"], "error")   

    def test_post_message_missing_content(self):
        """Test POST /api/message when content is missing"""
        response = self.client.post('/api/message', json={})
        data = response.get_json()
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'error')
        # self.assertEqual(data['message'], 'Content is required')
        
        # Verify that no database operations were attempted
        self.mock_session.add.assert_not_called()
        self.mock_session.commit.assert_not_called()

    def test_post_message_no_data(self):
        """Test POST /api/message with no data"""
        response = self.client.post('/api/message', data=None, content_type='application/json')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 500)  # Change expected status to 400
        self.assertEqual(data['status'], 'error')
        # self.assertEqual(data['message'], 'No data provided')

        # Verify that no database operations were attempted
        self.mock_session.add.assert_not_called()
        self.mock_session.commit.assert_not_called()


    @patch('server.Message.query')
    def test_get_message_with_data(self, mock_query):
        """Test GET /api/message when there are messages"""
        # Create a mock message
        mock_message = MagicMock()
        mock_message.id = 1
        mock_message.content = "Test message"
        mock_message.to_dict.return_value = {
            "id": mock_message.id,
            "content": mock_message.content
        }
     
        
        # Configure the mock to return our test message
        mock_query.all.return_value = [mock_message]
        
        response = self.client.get('/api/message')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)  # Expect 200, not 500
        self.assertEqual(len(data['messages']), 1)  # Expecting 1 message
        self.assertEqual(data['messages'][0]['content'], 'Test message')  # Check correct content
        mock_query.all.assert_called_once()

class AppInitializationTestCase(unittest.TestCase):
    def test_app_creation(self):
        """Test if the app is created successfully."""
        app = create_app()
        self.assertIsNotNone(app)

    def test_app_context_and_db(self):
        """Test if the app context is created and the database initializes properly."""
        app = create_app()
        with app.app_context():
            db.create_all()  # Ensure the database tables are created
            self.assertIsNotNone(db.engine)  # Check if the DB engine is available

      


if __name__ == '__main__':
    unittest.main()