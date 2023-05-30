import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import time
from utils import *


def add_data():
    payload_list = []
    while True:
        payload_str = get_random_payload_str()
        timestamp = datetime.now()
        payload_list.append((payload_str, timestamp.strftime("%Y-%m-%d %H:%M:%S")))
        if len(payload_list) == 10:
            insert_document_list(payload_list)
            payload_list = []
        time.sleep(1)


default_args = {
    "owner": "keshav137",
    "start_date": datetime.now(),
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "add_data_dag",
    default_args=default_args,
    description="Dag for adding a row in documents table every second",
    schedule_interval="@once",
    tags=["add_data"],
)

t1 = PythonOperator(
    task_id="add_data_dag",
    provide_context=True,
    python_callable=add_data,
    dag=dag,
)

t1
