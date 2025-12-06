'''  
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the Queue Listener for the clairgrid Grid Service.
'''

import json
import os
import time
import pika
from configuration_mixin import ConfigurationMixin

class QueueListener(ConfigurationMixin):
    """
    Listener for handling Grid Service requests via RabbitMQ.
    """
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.queue_name = f'grid_service_requests_{self.db_manager.db_name.lower()}'
        self.load_configuration()

    def load_configuration(self):
        """
        Loads configuration from environment variables.
        """
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        self.rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
        self.rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
        self.rabbitmq_password_file = os.getenv("RABBITMQ_PASSWORD_FILE")
        self.rabbitmq_password = self._read_password_file(self.rabbitmq_password_file, "RABBITMQ_PASSWORD_FILE")

    def on_request(self, ch, method, props, body):
        """
        Callback for handling incoming RabbitMQ messages.
        """
        print(f" [i] Received {props}", flush=True)
        response = None
        try:
            request = json.loads(body)
            correlation_id = props.correlation_id
            print(f" [>] {request=}", flush=True)
            if request['command'] == 'ping':
                response = {
                    "correlation_id": correlation_id,
                    "status": "success",
                    "message": f"Processed request {request['command']} on {self.db_manager.db_name}",
                    "request": request
                }
            else:
                response = {
                    "correlation_id": correlation_id,
                    "status": "error",
                    "message": "Unknown command",
                    "request": request
                }
            print(f" [<] {response=}", flush=True)
        except Exception as e:
            print(f" [x] Error processing request: {e}", flush=True)
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
        print(f"Connecting to queue {self.queue_name} at {self.rabbitmq_host}:{self.rabbitmq_port}...", flush=True)
        
        credentials = pika.PlainCredentials(self.rabbitmq_user, self.rabbitmq_password)
        parameters = pika.ConnectionParameters(
            host=self.rabbitmq_host,
            port=self.rabbitmq_port,
            credentials=credentials
        )

        connection = None
        while connection is None:
            try:
                connection = pika.BlockingConnection(parameters)
            except pika.exceptions.AMQPConnectionError:
                print(" [x] Queue not ready, retrying in 5 seconds...", flush=True)
                time.sleep(5)

        channel = connection.channel()
        channel.queue_declare(queue=self.queue_name)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=self.queue_name, on_message_callback=self.on_request)

        print(f" [.] Awaiting requests on queue {self.queue_name}", flush=True)
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
            connection.close()
