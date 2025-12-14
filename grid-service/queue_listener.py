'''  
    clairgrid : data structuration, presentation and navigation.
    Copyright David Lambert 2025

    This file contains the Queue Listener for the clairgrid Grid Service.
'''

import json
import os
import time
import pika
import metadata
from configuration_mixin import ConfigurationMixin
from decorators import echo
from authentication_manager import AuthenticationManager

class QueueListener(ConfigurationMixin):
    """
    Listener for handling Grid Service requests via RabbitMQ.
    """
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.authentication_manager = AuthenticationManager(db_manager)
        self.queue_name = f'grid_service_{self.db_manager.db_name.lower()}'
        self.load_configuration()
        self._init_command_handlers()

    def load_configuration(self):
        """
        Loads configuration from environment variables.
        """
        self.rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        self.rabbitmq_port = int(os.getenv("RABBITMQ_PORT", "5672"))
        self.rabbitmq_user = os.getenv("RABBITMQ_USER", "guest")
        self.rabbitmq_password_file = os.getenv("RABBITMQ_PASSWORD_FILE")
        self.rabbitmq_password = self._read_password_file(self.rabbitmq_password_file, "RABBITMQ_PASSWORD_FILE")

    def _init_command_handlers(self):
        self.command_handlers = {
            metadata.ActionInitialization: self._handle_nothing,
            metadata.ActionHeartbeat: self._handle_nothing,
            metadata.ActionAuthentication: self.authentication_manager.handle_authentication,
            metadata.ActionLoad: self._handle_load,
            metadata.ActionChangeGrid: self._handle_change_grid,
            metadata.ActionLocateGrid: self._handle_locate_grid,
            metadata.ActionPrompt: self._handle_prompt,
        }

    @echo
    def _handle_nothing(self, request):
        return { "status": metadata.SuccessStatus }

    @echo
    def _handle_load(self, request):
        return { "status": metadata.FailedStatus, "message": "Not implemented" }

    @echo
    def _handle_change_grid(self, request):
        return { "status": metadata.FailedStatus, "message": "Not implemented" }

    @echo
    def _handle_locate_grid(self, request):
        return { "status": metadata.FailedStatus, "message": "Not implemented" }

    @echo
    def _handle_prompt(self, request):
        return { "status": metadata.FailedStatus, "message": "Not implemented" }

    @echo
    def process_request(self, request):
        """
        Processes the parsed request using a dictionary of command handlers.
        """
        command = request.get('command')
        handler = self.command_handlers.get(command)
        
        if handler:
            return handler(request)
        else:
            return { "status": metadata.FailedStatus, "message": "Unknown command" }

    @echo
    def on_request(self, ch, method, props, body):
        """
        Callback for handling incoming RabbitMQ messages.
        """
        try:
            request = json.loads(body)
            reply = {
                "command": request['command'],
                "requestInitiatedOn": request['requestInitiatedOn'],
                "requestUuid": request['requestUuid'],
                "contextUuid": request['contextUuid'],
                "from": request['from'],
                "dbName": request['dbName']
            }
            if request.get('commandText'): reply['commandText'] = request['commandText']
            if request.get('url'): reply['url'] = request['url']
            if request.get('userUuid'): reply['userUuid'] = request['userUuid']
            if request.get('user'): reply['user'] = request['user']
            if request.get('jwt'): reply['jwt'] = request['jwt']
            try:
                print(f"<request {request}", flush=True)
                reply = reply | self.process_request(request)
                print(f">reply {reply}", flush=True)
            except Exception as e:
                reply = reply | {"status": "error", "can't process request, message": str(e)}
        except Exception as e:
            reply = {"status": "error", "message": f"invalid request: {str(e)}"}
            print(f">reply {reply}", flush=True)

        if props.reply_to and reply:
            reply["correlationId"] = props.correlation_id
            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,
                             properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=json.dumps(reply))
            ch.basic_ack(delivery_tag=method.delivery_tag)

    @echo
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
                print("Queue not ready, retrying in 5 seconds...", flush=True)
                time.sleep(5)

        channel = connection.channel()
        channel.queue_declare(queue=self.queue_name)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=self.queue_name, on_message_callback=self.on_request)

        print(f"Awaiting requests on queue {self.queue_name}", flush=True)
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
            connection.close()
