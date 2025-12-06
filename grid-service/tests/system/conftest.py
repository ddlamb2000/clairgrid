import pytest
import pika
import os
import json
import uuid
import time

@pytest.fixture(scope="session")
def rabbitmq_config():
    """
    Returns RabbitMQ configuration from environment variables or defaults.
    """
    with open(os.getenv("RABBITMQ_PASSWORD_FILE")) as f:
        password = f.read().strip()

    return {
        "host": os.getenv("RABBITMQ_HOST", "localhost"),
        "port": int(os.getenv("RABBITMQ_PORT", "5672")),
        "user": os.getenv("RABBITMQ_USER", "guest"),
        "password": password
    }

@pytest.fixture(scope="session")
def rabbitmq_connection(rabbitmq_config):
    """
    Establishes a connection to RabbitMQ for the test session.
    """
    credentials = pika.PlainCredentials(rabbitmq_config["user"], rabbitmq_config["password"])
    parameters = pika.ConnectionParameters(
        host=rabbitmq_config["host"],
        port=rabbitmq_config["port"],
        credentials=credentials
    )
    
    connection = None

    for _ in range(5):
        try:
            connection = pika.BlockingConnection(parameters)
            break
        except pika.exceptions.AMQPConnectionError:
            time.sleep(1)
            
    if not connection:
        pytest.fail("Could not connect to RabbitMQ")
        
    yield connection
    connection.close()

@pytest.fixture(scope="function")
def channel(rabbitmq_connection):
    """
    Provides a RabbitMQ channel for each test function.
    """
    channel = rabbitmq_connection.channel()
    yield channel
    if channel.is_open: channel.close()

@pytest.fixture(scope="function")
def rpc_client(channel):
    """
    A simple RPC client fixture that sets up a reply queue and provides a send_request method.
    """
    result = {}
    
    # Declare a temporary exclusive callback queue
    callback_queue = channel.queue_declare(queue='', exclusive=True).method.queue

    def on_response(ch, method, props, body):
        if props.correlation_id == result.get('corr_id'):
            result['response'] = json.loads(body)

    channel.basic_consume(
        queue=callback_queue,
        on_message_callback=on_response,
        auto_ack=True
    )

    def send_request(queue_name, payload, timeout=5):
        result['corr_id'] = str(uuid.uuid4())
        result['response'] = None
        
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            properties=pika.BasicProperties(
                reply_to=callback_queue,
                correlation_id=result['corr_id'],
                content_type='application/json'
            ),
            body=json.dumps(payload)
        )
        
        start_time = time.time()
        while result['response'] is None:
            connection = channel.connection
            connection.process_data_events()
            if time.time() - start_time > timeout:
                raise TimeoutError("Timed out waiting for RPC response")
                
        return result['response']

    return send_request

