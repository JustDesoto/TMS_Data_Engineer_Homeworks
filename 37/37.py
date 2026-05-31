from airflow.operators.python import PythonOperator,BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import DAG
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def log_stats(**kwargs):
    ti = kwargs['ti']
    stats = ti.xcom_pull(task_ids='calculate_stats')
    

    for row in stats:
        logger.info(f"run_id: {row[0]}")
        logger.info(f"Количество строк: {row[1]}")
        logger.info(f"Общая сумма: {row[2]}")
        logger.info(f"Минимальная сумма: {row[3]}")
        logger.info(f"Максимальная сумма: {row[4]}")
        logger.info(f"Средняя сумма: {row[5]}")

with DAG(
    dag_id='37_home_work',
    start_date=datetime(2026,4,23),
    schedule=None,
    catchup=False,
    tags=["lesson37"]
) as dag:
    create_schema_with_tables = PostgresOperator(
        task_id="create_schema_with_tables",
        postgres_conn_id="my_postgres_conn",
        sql="""
            CREATE SCHEMA IF NOT EXISTS raw;
            CREATE TABLE IF NOT EXISTS raw.lesson37_source_sales (
            run_id TEXT NOT NULL,
            order_id TEXT NOT NULL,
            amount NUMERIC(10,2) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            PRIMARY KEY (run_id, order_id)
        );
            """
    )

    generate_data = PostgresOperator(
        task_id="generate_data",
        postgres_conn_id="my_postgres_conn",
        sql="""
            INSERT INTO raw.lesson37_source_sales (run_id, order_id, amount)
            SELECT
            %(run_id)s,
            'ord_' || gs::text,
            round((random() * 90 + 10)::numeric, 2)
            FROM generate_series(1, 20) gs
            """,
        parameters={"run_id": "{{run_id}}"}
    )

    calculate_stats = PostgresOperator(
        task_id="calculate_stats",
        postgres_conn_id="my_postgres_conn",
        sql="""
            CREATE SCHEMA IF NOT EXISTS mart;
            CREATE TABLE IF NOT EXISTS mart.lesson37_sales_stats (
                run_id TEXT PRIMARY KEY,
                rows_count INTEGER NOT NULL,
                total_amount NUMERIC(12,2) NOT NULL,
                min_amount NUMERIC(10,2) NOT NULL,
                max_amount NUMERIC(10,2) NOT NULL,
                avg_amount NUMERIC(10,2) NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            
            INSERT INTO mart.lesson37_sales_stats (run_id, rows_count, total_amount, min_amount, max_amount, avg_amount)
            SELECT
                run_id,
                COUNT(*) as rows_count,
                SUM(amount) as total_amount,
                MIN(amount) as min_amount,
                MAX(amount) as max_amount,
                ROUND(AVG(amount), 2) as avg_amount
            FROM raw.lesson37_source_sales
            WHERE run_id = %(run_id)s
            GROUP BY run_id

            
            RETURNING 
                run_id,
                rows_count,
                total_amount,
                min_amount,
                max_amount,
                avg_amount;
        """,
        parameters={"run_id": "{{ run_id }}"}
    )

    
    log_stats_task = PythonOperator(
        task_id="log_stats",
        python_callable=log_stats
    )

    create_schema_with_tables >> generate_data >> calculate_stats >> log_stats_task
