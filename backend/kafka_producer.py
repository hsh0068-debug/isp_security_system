from kafka import KafkaProducer
import json
import logging

logger = logging.getLogger(__name__)

# ─── KAFKA PRODUCER ──────────────────────────────────────────────
# This sends login events to the Kafka topic in real time
# Just like Dialog/SLT would stream millions of login events

producer = None

def get_producer():
    global producer
    if producer is None:
        try:
            producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                retries=3,
                request_timeout_ms=5000,
                api_version=(3, 9, 2)
            )
            print("Kafka Producer connected successfully!")
        except Exception as e:
            print(f"Kafka not available: {e}")
            producer = None
    return producer

def publish_login_event(event_data: dict):
    """
    Publish a login event to the Kafka 'login-events' topic
    This is the real-time streaming component of our ISP security system
    """
    try:
        p = get_producer()
        if p:
            future = p.send(
                'login-events',
                key=event_data.get('username', 'unknown'),
                value=event_data
            )
            p.flush()
            record_metadata = future.get(timeout=5)
            print(f"Event published to Kafka: topic={record_metadata.topic}, partition={record_metadata.partition}, offset={record_metadata.offset}")
            return True
        else:
            print("Kafka not available — event saved to database only")
            return False
    except Exception as e:
        print(f"Kafka publish error: {e}")
        return False

def close_producer():
    global producer
    if producer:
        producer.close()
        producer = None