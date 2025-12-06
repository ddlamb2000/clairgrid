import pytest
import uuid

# The queue name matches the expectation for a DB named 'tests'
# queue_name = f'grid_service_requests_{db_name.lower()}'
TARGET_QUEUE = "grid_service_requests_clairgrid_test"

def test_ping_service(rpc_client):
    """
    Test that the service is reachable and responds to a basic request.
    Assumes the service is running and listening on 'grid_service_requests_tests'.
    """
    payload = {
        "command": "ping",
        "data": {
            "timestamp": "2023-10-27T10:00:00Z"
        }
    }
    
    try:
        response = rpc_client(TARGET_QUEUE, payload, timeout=5)
        
        assert response is not None
        assert "status" in response
        assert response["status"] == "success"
        # Based on current placeholder logic in queue_listener.py:
        # "message": f"Processed request on {self.db_manager.db_name}"
        assert "Processed request" in response["message"]
        assert response["data"] == payload
        
    except TimeoutError:
        pytest.fail(f"Service did not respond on queue {TARGET_QUEUE}. Is the service running with DB_NAME=tests?")

def test_invalid_json(channel):
    """
    Test sending invalid JSON. 
    Note: The rpc_client fixture handles JSON serialization automatically, 
    so we use the raw channel here to send bad data.
    """
    # Create a temporary reply queue
    result = {}
    callback_queue = channel.queue_declare(queue='', exclusive=True).method.queue
    corr_id = str(uuid.uuid4())

    def on_response(ch, method, props, body):
        if props.correlation_id == corr_id:
            result['response'] = body # Keep as raw bytes or try parse

    channel.basic_consume(queue=callback_queue, on_message_callback=on_response, auto_ack=True)

    # Send invalid JSON
    channel.basic_publish(
        exchange='',
        routing_key=TARGET_QUEUE,
        properties=pika.BasicProperties(
            reply_to=callback_queue,
            correlation_id=corr_id
        ),
        body="This is not JSON"
    )

    # Wait for response
    import time
    start = time.time()
    while 'response' not in result and time.time() - start < 5:
        channel.connection.process_data_events()

    if 'response' not in result:
        pytest.fail("Service did not respond to invalid JSON")

    # The service returns a JSON with status error for exceptions
    import json
    response_data = json.loads(result['response'])
    assert response_data['status'] == 'error'

