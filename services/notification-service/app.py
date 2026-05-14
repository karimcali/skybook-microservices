from flask import Flask, jsonify
import pika
import json
import os
import time
import threading

app = Flask(__name__)

notifications = {}

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
QUEUE_NAME = "notification_booking_confirmed"


@app.get("/health")
def health():
    return jsonify({
        "service": "notification-service",
        "status": "ok"
    })


@app.get("/notifications/<booking_id>")
def get_notification(booking_id):
    notification = notifications.get(booking_id)

    if not notification:
        return jsonify({"error": "Notification not found"}), 404

    return jsonify(notification)


def handle_message(channel, method, properties, body):
    try:
        event = json.loads(body)

        booking_id = event.get("booking_id")

        if not booking_id:
            print("Event ignored because booking_id is missing")
            channel.basic_ack(delivery_tag=method.delivery_tag)
            return

        notification = {
            "notification_id": "NOTIFICATION-" + booking_id,
            "booking_id": booking_id,
            "passenger_name": event.get("passenger_name"),
            "message": "Booking confirmed for " + event.get("passenger_name", "passenger"),
            "status": "sent"
        }

        notifications[booking_id] = notification

        print("Notification created:", notification)

        channel.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as error:
        print("Error handling notification event:", error)
        channel.basic_ack(delivery_tag=method.delivery_tag)


def consume_events():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST)
            )

            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME)

            channel.basic_consume(
                queue=QUEUE_NAME,
                on_message_callback=handle_message
            )

            print("notification-service is waiting for booking events")
            channel.start_consuming()

        except Exception as error:
            print("Could not connect to RabbitMQ:", error)
            time.sleep(5)


if __name__ == "__main__":
    consumer_thread = threading.Thread(target=consume_events)
    consumer_thread.daemon = True
    consumer_thread.start()

    app.run(host="0.0.0.0", port=5005)