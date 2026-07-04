from kafka import KafkaConsumer
import json
import threading
import logging

logger = logging.getLogger(__name__)

def start_login_event_consumer():
    """
    Background consumer that reads login events from Kafka
    and processes them for the security monitoring system
    """
    def consume():
        try:
            consumer = KafkaConsumer(
                'login-events',
                bootstrap_servers=['localhost:9092'],
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='isp-security-group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                api_version=(3, 9, 2),
                consumer_timeout_ms=1000
            )
            print("Kafka Consumer started — listening for login events...")
            
            for message in consumer:
                event = message.value
                print(f"Kafka received login event: user={event.get('username')} risk={event.get('risk_score')} action={event.get('action')}")
                
        except Exception as e:
            print(f"Kafka consumer error: {e}")

    # Run consumer in background thread
    thread = threading.Thread(target=consume, daemon=True)
    thread.start()
    return thread