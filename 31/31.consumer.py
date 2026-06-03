from confluent_kafka import Consumer
import json
import psycopg2
import time

conn = psycopg2.connect(
    host="localhost", port=5432, dbname="events_db", user="user", password="password"
)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS login_events (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        event_time TIMESTAMP NOT NULL,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS logout_events (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        event_time TIMESTAMP NOT NULL,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

conn.commit()


kafka_conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'user_events_group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
}

consumer = Consumer(kafka_conf)
consumer.subscribe(['user_events'])

try:
    while (True):
        msg = consumer.poll(1.0)

        if msg is None:
            continue
        
        if msg.error():
            print(f"Ошибка: {msg.error()}")
            continue

        event = json.loads(msg.value().decode('utf-8'))
        user_id = event['user_id']
        event_type = event['event']
        event_time = event['timestamp']

        if event_type == 'login':
            cursor.execute(
                "INSERT INTO login_events (user_id, event_time) VALUES (%s, %s)",
                (user_id, event_time)
            )
            print(f"Login: user {user_id}")

        if event_type == 'logout':
            cursor.execute(
                "INSERT INTO logout_events (user_id, event_time) VALUES (%s, %s)",
                (user_id, event_time)
            )
            print(f"Logout: user {user_id}")

        if event_type != 'login' and event_type != 'logout':
            print(f"Error: invalid event_type")

        # Коммитим все наши события 
        conn.commit()
        consumer.commit(msg)

except KeyboardInterrupt:
    print("\nОстановлено ручным вводом")
finally:
    consumer.close()
    cursor.close()
    conn.close()