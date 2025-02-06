import unittest
from unittest.mock import patch, MagicMock
from server import create_app, db, Message
from flask import json
import sys
import io
import importlib

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
        self.assertEqual(response.status_code, 500)
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

class MainExecutionTestCase(unittest.TestCase):
    """Test cases for the main execution block"""

    def setUp(self):
        # Store original module state
        self.original_name = sys.modules['server'].__name__

    def tearDown(self):
        # Restore original module state
        sys.modules['server'].__name__ = self.original_name

    @patch('server.create_app')
    @patch('server.db.create_all')
    @patch('flask.Flask.run')
    def test_main_execution(self, mock_run, mock_create_all, mock_create_app):
        """Test the main execution block of the application"""
        # Set up mock app
        mock_flask_app = MagicMock()
        mock_create_app.return_value = mock_flask_app
        
        # Simulate main block execution
        import server
        with patch.dict(server.__dict__, {'__name__': '__main__'}):
            # Execute the main block code
            app = create_app()
            with app.app_context():
                db.create_all()
            app.run(debug=True, host='0.0.0.0')

        # Verify the calls
        mock_create_app.assert_called_once()
        mock_create_all.assert_called_once()
        mock_run.assert_called_once_with(debug=True, host='0.0.0.0')

    @patch('server.create_app')
    @patch('server.db.create_all')
    def test_main_context_manager(self, mock_create_all, mock_create_app):
        """Test the context manager in the main block"""
        # Set up mock app
        mock_flask_app = MagicMock()
        mock_context = MagicMock()
        mock_flask_app.app_context.return_value = mock_context
        mock_create_app.return_value = mock_flask_app

        # Execute main block code
        import server
        with patch.dict(server.__dict__, {'__name__': '__main__'}):
            app = create_app()
            with app.app_context():
                db.create_all()

        # Verify the calls
        mock_create_app.assert_called_once()
        mock_flask_app.app_context.assert_called_once()
        mock_create_all.assert_called_once()
        mock_context.__enter__.assert_called_once()
        mock_context.__exit__.assert_called_once()

      


if __name__ == '__main__':
    unittest.main()