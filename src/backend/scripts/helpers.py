import random
import psycopg2
import json

BUSINESS_IDS = ["walgreens", "cvs", "traderjoes", "safeway", "walmart"]


def get_connection():
    return psycopg2.connect(
        host="127.0.0.1",
        database="veryfidev",
        user="keshav137",
        port="5432",
        password="****",
    )


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
    return payload_str


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


def rand_payload():
    return {
        "value": random.randint(0, 100),
        "score": random.randrange(15, 100),
        "ocr_score": random.randrange(15, 100),
        "bounding_box": [round(random.random(), 2) for i in range(4)],
    }
