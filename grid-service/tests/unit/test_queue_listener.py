import unittest
import json
from unittest.mock import MagicMock, patch, ANY
import pika
from queue_listener import QueueListener

class TestQueueListener(unittest.TestCase):

    @patch("queue_listener.os.getenv")
    @patch("queue_listener.QueueListener._read_password_file")
    def setUp(self, mock_read_pwd, mock_getenv):
        mock_getenv.side_effect = lambda key, default=None: {
            "RABBITMQ_HOST": "localhost",
            "RABBITMQ_PORT": "5672",
            "RABBITMQ_USER": "guest",
            "RABBITMQ_PASSWORD_FILE": "/secrets/rmq_pass"
        }.get(key, default)
        
        mock_read_pwd.return_value = "guest_pass"
        
        self.mock_db_manager = MagicMock()
        self.mock_db_manager.db_name = "TEST_DB"
        
        self.listener = QueueListener(self.mock_db_manager)

    def test_init_config(self):
        """Test configuration loading in init."""
        self.assertEqual(self.listener.rabbitmq_host, "localhost")
        self.assertEqual(self.listener.queue_name, "grid_service_requests_test_db")

    def test_on_request_success(self):
        """Test on_request handling a valid message."""
        # Setup mocks
        mock_ch = MagicMock()
        mock_method = MagicMock()
        mock_props = MagicMock()
        mock_props.reply_to = "reply_queue"
        mock_props.correlation_id = "123"
        
        body = json.dumps({"action": "test"}).encode('utf-8')
        
        self.listener.on_request(mock_ch, mock_method, mock_props, body)
        
        # Verify response published
        mock_ch.basic_publish.assert_called_once()
        args, kwargs = mock_ch.basic_publish.call_args
        
        # Check routing key
        self.assertEqual(kwargs['routing_key'], "reply_queue")
        
        # Check properties
        self.assertEqual(kwargs['properties'].correlation_id, "123")
        
        # Check body
        response = json.loads(kwargs['body'])
        self.assertEqual(response['status'], 'success')
        self.assertEqual(response['data']['action'], 'test')
        
        # Verify ack
        mock_ch.basic_ack.assert_called_once_with(delivery_tag=mock_method.delivery_tag)

    def test_on_request_error(self):
        """Test on_request handling invalid JSON."""
        mock_ch = MagicMock()
        mock_method = MagicMock()
        mock_props = MagicMock()
        mock_props.reply_to = "reply_queue"
        
        body = b"invalid json"
        
        self.listener.on_request(mock_ch, mock_method, mock_props, body)
        
        # Verify error response published
        mock_ch.basic_publish.assert_called_once()
        args, kwargs = mock_ch.basic_publish.call_args
        
        response = json.loads(kwargs['body'])
        self.assertEqual(response['status'], 'error')
        
        # Verify ack
        mock_ch.basic_ack.assert_called_once()

    @patch("queue_listener.pika.BlockingConnection")
    @patch("queue_listener.time.sleep")
    def test_start_connection_retry(self, mock_sleep, mock_blocking_conn):
        """Test that start retries connection on failure."""
        # First attempt raises error, second succeeds
        mock_connection = MagicMock()
        mock_blocking_conn.side_effect = [pika.exceptions.AMQPConnectionError, mock_connection]
        
        # Mock channel to avoid infinite loop or errors downstream
        mock_channel = MagicMock()
        mock_connection.channel.return_value = mock_channel
        
        # Stop consuming immediately to exit start()
        mock_channel.start_consuming.side_effect = KeyboardInterrupt
        
        try:
            self.listener.start()
        except KeyboardInterrupt:
            pass # Expected from our side_effect
            
        self.assertEqual(mock_blocking_conn.call_count, 2)
        mock_sleep.assert_called_once_with(5)
        
    @patch("queue_listener.pika.BlockingConnection")
    def test_start_setup(self, mock_blocking_conn):
        """Test successful start setup."""
        mock_connection = MagicMock()
        mock_blocking_conn.return_value = mock_connection
        mock_channel = MagicMock()
        mock_connection.channel.return_value = mock_channel
        
        # Exit loop
        mock_channel.start_consuming.side_effect = KeyboardInterrupt
        
        try:
            self.listener.start()
        except KeyboardInterrupt:
            pass
            
        # Check declarations
        mock_channel.queue_declare.assert_called_with(queue=self.listener.queue_name)
        mock_channel.basic_qos.assert_called_with(prefetch_count=1)
        mock_channel.basic_consume.assert_called_with(
            queue=self.listener.queue_name, 
            on_message_callback=self.listener.on_request
        )

