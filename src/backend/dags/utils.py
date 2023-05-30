import os
from sqlalchemy import create_engine, text
import json
import random
import psycopg2
import statistics

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://keshav137:*****@138.197.208.92:5432/veryfidev"
)
engine = create_engine(DATABASE_URI)
batch_size = 5000
BUSINESS_IDS = ["walgreens", "cvs", "traderjoes", "safeway", "walmart"]


def rand_payload():
    return {
        "value": random.randint(0, 100),
        "score": random.randrange(60, 100),
        "ocr_score": random.randrange(60, 100),
        "bounding_box": [round(random.random(), 2) for i in range(4)],
    }


def get_connection():
    return psycopg2.connect(
        host="138.197.208.92",
        database="veryfidev",
        user="keshav137",
        port="5432",
        password="******",
    )


def insert_document_list(document_list):
    """insert multiple ml responses into the documents table"""
    sql = "INSERT INTO documents(ml_response, timestamp) VALUES(%s,%s)"
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.executemany(sql, document_list)
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def get_average(arr):
    return round(sum(arr) / len(arr), 2)


def get_random_payload_str():
    items = [rand_payload() for i in range(0, 9)]
    values, scores, ocr_scores = [], [], []
    for item in items:
        values.append(item["value"])
        scores.append(item["score"])
        ocr_scores.append(item["ocr_score"])

    payload = {"business_id": BUSINESS_IDS[random.randint(0, len(BUSINESS_IDS) - 1)]}

    payload["line_items"] = items
    payload["total"] = {
        "value": sum(values),
        "score": get_average(scores),
        "ocr_score": get_average(ocr_scores),
    }
    payload_str = json.dumps(payload)
    print(payload_str)
    return payload_str


"""
Parameters
----------
interval : 'minute' or 'hour'
    Specifies what type of aggregation to use
for_live : boolean
    Whether this processing is for live data or past data
duration : Number of minutes in the past to process data for when processing is for live data
    
"""


def process_data(interval, for_live, duration):
    with engine.begin() as connection:
        if for_live:
            sql = f"SELECT COUNT(*) FROM documents WHERE timestamp >= NOW() - INTERVAL '{duration} minutes'"
        else:
            sql = "SELECT COUNT(*) FROM documents"
        result = connection.execute(sql)
        total_rows = result.fetchone()[0]
        for offset in range(0, total_rows, batch_size):
            if for_live:
                sql = f"""
          SELECT * FROM documents
          WHERE timestamp >= NOW() - INTERVAL '{duration} minutes'
          ORDER BY timestamp DESC;
        """
            else:
                sql = text(
                    f"""
          SELECT * FROM documents
          ORDER BY timestamp DESC 
          LIMIT {batch_size} 
          OFFSET {offset}
        """
                )
            result = connection.execute(sql)
            batch_data = result.fetchall()
            mapping = {}
            for row in batch_data:
                ml_response = json.loads(row[1])
                if interval == "minute":
                    timestamp = row[2].strftime(
                        "%Y-%m-%d %H:%M"
                    )  # stripping the seconds value from timestamp
                    table_name = "minutely_parsed_total"
                else:
                    timestamp = (
                        row[2].strftime("%Y-%m-%d %H") + ":00"
                    )  # stripping second and minute values
                    table_name = "hourly_parsed_total"

                key = timestamp + "_" + ml_response["business_id"]
                if key not in mapping:
                    mapping[key] = {
                        "business_id": ml_response["business_id"],
                        "ts": timestamp,
                        "amounts": [],
                        "scores": [],
                        "ocr_scores": [],
                    }
                mapping[key]["amounts"].append(ml_response["total"]["value"])
                mapping[key]["scores"].append(ml_response["total"]["score"])
                mapping[key]["ocr_scores"].append(ml_response["total"]["ocr_score"])

            data_to_insert = []
            for key in mapping:
                value = mapping[key]
                entry = (
                    sum(value["amounts"]),
                    get_average(value["scores"]),
                    get_average(value["ocr_scores"]),
                    round(statistics.median(value["scores"]), 2),
                    round(statistics.median(value["ocr_scores"]), 2),
                    value["ts"],
                    value["business_id"],
                )
                data_to_insert.append(entry)

            if len(data_to_insert):
                values = ", ".join(map(str, data_to_insert))
                sql = (
                    "INSERT INTO "
                    + table_name
                    + "(total_amount, avg_score, avg_ocr_score, median_score, median_ocr_score, ts, business_id) VALUES {}".format(
                        values
                    )
                )
                print("inserting values: ", len(data_to_insert))
                connection.execute(sql)
