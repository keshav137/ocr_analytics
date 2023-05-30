import pandas as pd
from helpers import *
from datetime import datetime, timedelta

# Generating data for the past 7 days
timestamps = pd.date_range(end=datetime.now(), freq="S", periods=24 * 60 * 60 * 7)

payload_list = []
for timestamp in timestamps:
    payload_str = get_random_payload_str()
    payload_list.append((payload_str, timestamp.strftime("%Y-%m-%d %H:%M:%S")))

insert_document_list(payload_list)
