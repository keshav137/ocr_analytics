import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from utils import *

default_args = {
    "owner": "keshav137",
    "start_date": datetime.now() - timedelta(hours=1),
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "live_hourly_dag",
    default_args=default_args,
    description="Runs every 60 minutes and processes hourly data for the past 60 minutes",
    schedule_interval="0 * * * *",
    tags=["live_hourly"],
)

t1 = PythonOperator(
    task_id="process_data",
    provide_context=True,
    python_callable=process_data,
    op_args=["hour", True, "60"],
    dag=dag,
)

t1
