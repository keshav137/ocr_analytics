from flask import Flask, jsonify, request
import psycopg2
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)


def get_db_connection():
    conn = psycopg2.connect(
        dbname="veryfidev",
        user="keshav137",
        password="*****",
        host="138.197.208.92",
        port="5432",
    )
    return conn


# Endpoint for retrieving unique business_id values from hourly_parsed_total table
@app.route("/api/business_ids", methods=["GET"])
def get_business_ids():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT DISTINCT business_id FROM hourly_parsed_total")
        results = cursor.fetchall()
        business_ids = [result[0] for result in results]
        cursor.close()
        connection.close()
        return jsonify(business_ids)

    except (Exception, psycopg2.Error) as error:
        print("Error retrieving business_ids:", error)
        return jsonify([])


# Endpoint for retrieving data from minutely_parsed_total table between start_time and end_time values for an optional business_id
# If business_id is not provided, then data for all business_ids is returned
@app.route("/api/minutedata", methods=["POST"])
def get_minute_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    data = request.get_json()
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    business_id = data.get("business_id")

    query = """
        SELECT * FROM minutely_parsed_total
        WHERE ts BETWEEN %s AND %s
    """
    params = [start_time, end_time]

    if business_id is not None:
        query += " AND business_id = %s"
        params.append(business_id)

    cursor.execute(query, params)
    data = cursor.fetchall()

    result = [
        {
            "total_amount": row[1],
            "avg_score": row[2],
            "avg_ocr_score": row[3],
            "median_score": row[4],
            "median_ocr_score": row[5],
            "ts": row[6],
            "business_id": row[7],
        }
        for row in data
    ]

    cursor.close()
    conn.close()
    return jsonify(result)


# Endpoint for retrieving data from hourly_parsed_total table between start_time and end_time values for an optional business_id
# If business_id is not provided, then data for all business_ids is returned
@app.route("/api/hourdata", methods=["POST"])
def get_hour_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    data = request.get_json()
    start_time = data.get("start_time")
    end_time = data.get("end_time")
    business_id = data.get("business_id")

    query = """
        SELECT * FROM hourly_parsed_total
        WHERE ts BETWEEN %s AND %s
    """
    params = [start_time, end_time]

    if business_id is not None:
        query += " AND business_id = %s"
        params.append(business_id)

    cursor.execute(query, params)
    data = cursor.fetchall()
    result = [
        {
            "total_amount": row[1],
            "avg_score": row[2],
            "avg_ocr_score": row[3],
            "median_score": row[4],
            "median_ocr_score": row[5],
            "ts": row[6],
            "business_id": row[7],
        }
        for row in data
    ]
    cursor.close()
    conn.close()
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
