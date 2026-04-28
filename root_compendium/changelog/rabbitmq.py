import json
import logging

import pika
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_connection_params():
    host = getattr(settings, 'RABBITMQ_HOST', 'localhost')
    port = getattr(settings, 'RABBITMQ_PORT', 5672)
    user = getattr(settings, 'RABBITMQ_USER', '')
    password = getattr(settings, 'RABBITMQ_PASSWORD', '')
    if user and password:
        credentials = pika.PlainCredentials(user, password)
        return pika.ConnectionParameters(host=host, port=port, credentials=credentials)
    return pika.ConnectionParameters(host=host, port=port)


def publish_status_change(payload, queue_name=None):
    queue = queue_name or getattr(settings, 'RABBITMQ_QUEUE', 'change_request_status')
    try:
        connection = pika.BlockingConnection(_get_connection_params())
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True)
        body = json.dumps(payload).encode('utf-8')
        channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2),
        )
        connection.close()
        return True
    except Exception as exc:
        logger.warning('RabbitMQ publish failed: %s', exc)
        return False


def consume_status_changes(callback, queue_name=None):
    queue = queue_name or getattr(settings, 'RABBITMQ_QUEUE', 'change_request_status')
    connection = pika.BlockingConnection(_get_connection_params())
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)

    def _on_message(channel, method, properties, body):
        payload = json.loads(body.decode('utf-8'))
        callback(payload)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=_on_message)
    channel.start_consuming()
