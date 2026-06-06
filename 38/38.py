import random

from airflow.operators.python import PythonOperator,BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from uuid import uuid4
from airflow.models import Variable
from airflow.decorators import dag, task
from pymongo import MongoClient

from airflow.models import DAG
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


@dag(
    dag_id='38_home_work_generator',
    start_date=datetime(2026,4,23),
    schedule="*/2 * * * *",
    catchup=False,
    tags=["lesson38"]
)
def lesson_38():
    @task
    def generate_events():
        cfg = Variable.get("lesson38_mongo_url")

        user_pull = [f"student_user_{id:04d}" for id in range(1,301)]
        event_types = ["view", "comment", "send_hw", "question"]
        event_weights = [0.75, 0.02, 0.07, 0.15]
        rows = []
        for _ in range(200):
            rows.append({
                "event_id": str(uuid4()),
                "event_type": random.choices(event_types, weights=event_weights,k=1)[0],
                "user_login": random.choice(user_pull),
                "event_ts": datetime.now(timezone.utc).isoformat()

            })

        with MongoClient(cfg) as client:
            coll = client["source_db"]["events_stream"]
            inserted = coll.insert_many(rows,ordered=False)
        logger.info(f"Вставлено {len(inserted.inserted_ids)} строк")

    generate_events()

@dag(
    dag_id='38_home_work_transform',
    start_date=datetime(2026,4,23),
    schedule="*/5 * * * *",
    catchup=False,
    tags=["lesson38"]
)
def lesson38_transform():
    @task
    def load_raw(**kwargs):
        cfg = Variable.get("lesson38_mongo_url")
        context = kwargs
        window_start = context["data_interval_start"].in_timezone("UTC")
        window_end = context["data_interval_end"].in_timezone("UTC")

        logger.info(f"[!] Extract with window {window_start} - {window_end}")

        with MongoClient(cfg) as client:
            coll = client["source_db"]["events_stream"]

            rows = list(
                coll.find(
                    {
                        "event_ts": {
                            "$gte": window_start.isoformat(),
                            "$lt": window_end.isoformat()
                        }
                    }
                )
            )

            norm_rows = []
            for row in rows:
                norm_rows.append(
                    [
                        str(row["event_id"]),
                        str(row["event_type"]),
                        str(row["user_login"]),
                        str(row["event_ts"])
                    ]
                )

            hook = PostgresHook(postgres_conn_id="warehouse_postgres_conn")
            hook.run("""
            CREATE SCHEMA IF NOT EXISTS raw;
            CREATE TABLE IF NOT EXISTS raw.events (
                     event_id TEXT PRIMARY KEY,
                     event_type TEXT,
                     user_login TEXT,
                     event_ts TIMESTAMPTZ,
                     tech_load_at TIMESTAMPTZ default now())
                """)
            
            sql = """
                INSERT INTO raw.events(event_id, event_type, user_login, event_ts)
                values (%s,%s,%s,%s)
                    ON CONFLICT (event_id) DO UPDATE SET
                    event_type = EXCLUDED.event_type,
                    user_login = EXCLUDED.user_login,
                    event_ts = EXCLUDED.event_ts,
                    tech_load_at = now();
                """
            
            conn = hook.get_conn()
            with conn.cursor() as cursor:
                cursor.executemany(sql,norm_rows)
            conn.commit()
            conn.close()



    @task
    def load_dds(**kwargs):
        
        context = kwargs
        window_start = context["data_interval_start"].in_timezone("UTC")
        window_end = context["data_interval_end"].in_timezone("UTC")
        
        
        logger.info(f"Загрузка в DDS за период: {window_start} - {window_end}")
        
        hook = PostgresHook(postgres_conn_id="warehouse_postgres_conn")

        hook.run("""
            CREATE SCHEMA IF NOT EXISTS dds;
            
            CREATE TABLE IF NOT EXISTS dds.dim_users (
                user_id SERIAL PRIMARY KEY,
                user_login TEXT UNIQUE NOT NULL,
                created_at TIMESTAMPTZ DEFAULT now()
            );
            
            CREATE TABLE IF NOT EXISTS dds.dim_event_types (
                event_type_id SERIAL PRIMARY KEY,
                event_type_name TEXT UNIQUE NOT NULL
            );
            
            CREATE TABLE IF NOT EXISTS dds.fact_events (
                event_id TEXT PRIMARY KEY,
                user_id INTEGER REFERENCES dds.dim_users(user_id),
                event_type_id INTEGER REFERENCES dds.dim_event_types(event_type_id),
                event_ts TIMESTAMPTZ NOT NULL,
                tech_load_at TIMESTAMPTZ DEFAULT now()
            );
            
            INSERT INTO dds.dim_event_types (event_type_name)
            VALUES ('view'), ('comment'), ('send_hw'), ('question')
            ON CONFLICT (event_type_name) DO NOTHING;
        """)
        
        hook.run(f"""
            INSERT INTO dds.dim_users (user_login)
            SELECT DISTINCT user_login 
            FROM raw.events 
            WHERE event_ts >= '{window_start.isoformat()}' 
              AND event_ts < '{window_end.isoformat()}'
              AND user_login NOT IN (SELECT user_login FROM dds.dim_users)
            ON CONFLICT (user_login) DO NOTHING;
        """)
        
        hook.run(f"""
            INSERT INTO dds.fact_events (event_id, user_id, event_type_id, event_ts)
            SELECT 
                r.event_id,
                u.user_id,
                et.event_type_id,
                r.event_ts
            FROM raw.events r
            JOIN dds.dim_users u ON r.user_login = u.user_login
            JOIN dds.dim_event_types et ON r.event_type = et.event_type_name
            WHERE r.event_ts >= '{window_start.isoformat()}' 
              AND r.event_ts < '{window_end.isoformat()}'
            ON CONFLICT (event_id) DO UPDATE SET
                user_id = EXCLUDED.user_id,
                event_type_id = EXCLUDED.event_type_id,
                event_ts = EXCLUDED.event_ts,
                tech_load_at = now();
        """)
        logger.info(f"DDS слой обновлен для интервала {window_start} - {window_end}")

        
    load_raw() >> load_dds()

lesson_38()
lesson38_transform()
