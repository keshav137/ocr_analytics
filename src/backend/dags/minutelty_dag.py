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
    "minutely_dag",
    default_args=default_args,
    description="Dag for processing secondly data from documents table in batches, aggregating it \
  into minutely values and storing them in minutely_parsed_total table",
    schedule_interval="@once",
    tags=["example"],
)

t1 = PythonOperator(
    task_id="process_data",
    provide_context=True,
    python_callable=process_data,
    op_args=["minute", False, None],
    dag=dag,
)

t1
