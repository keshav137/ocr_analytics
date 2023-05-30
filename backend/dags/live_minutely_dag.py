import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from utils import *

default_args = {
    "owner": "keshav137",
    "start_date": datetime.now(),
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "live_minutely_dag",
    default_args=default_args,
    description="Runs every 5 minutes and processes minutely data for the past 5 minutes",
    schedule_interval="*/5  * * * *",
    tags=["example"],
)

t1 = PythonOperator(
    task_id="process_data",
    provide_context=True,
    python_callable=process_data,
    op_args=["minute", True, "5"],
    dag=dag,
)

t1
