import json
import os
import time
import pika

class QueueListener:
    """
    Listener for handling Grid Service requests via RabbitMQ.
    """
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        self.queue_name = 'grid_service_requests'

    def on_request(self, ch, method, props, body):
        """
        Callback for handling incoming RabbitMQ messages.
        """
        print(f" [.] Received {body}", flush=True)
        response = None
        try:
            request = json.loads(body)
            # Placeholder: Implement actual request handling logic here
            response = {
                "status": "success",
                "message": f"Processed request for {self.db_manager.db_name}",
                "data": request
            }
        except Exception as e:
            print(f"Error processing request: {e}", flush=True)
            response = {"status": "error", "message": str(e)}

        if props.reply_to:
            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,
                             properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=json.dumps(response))
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def start(self):
        """
        Starts the RabbitMQ consumer.
        """
        print(f"Connecting to RabbitMQ at {self.rabbitmq_host}...", flush=True)
        connection = None
        while connection is None:
            try:
                connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbitmq_host))
            except pika.exceptions.AMQPConnectionError:
                print("RabbitMQ not ready, retrying in 5 seconds...", flush=True)
                time.sleep(5)

        channel = connection.channel()
        channel.queue_declare(queue=self.queue_name)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=self.queue_name, on_message_callback=self.on_request)

        print(" [x] Awaiting RPC requests", flush=True)
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
            connection.close()
