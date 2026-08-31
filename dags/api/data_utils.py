import json
from typing import Any, Dict

import requests
from datawarehouse.dwh_utils import get_conn_cursor, close_conn_cursor


def load_json_to_postgres(data, data_origin):

    table_mapping = {
        "yt_data": "videos_data_json",
    }

    table_name = table_mapping.get(data_origin, f"{data_origin}_json")

    # Connect to PostgreSQL via Airflow Hook
    conn, cur = get_conn_cursor()

    try:
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")

        # Create temporary table to load json
        # Generic structure: stores JSON as JSONB
        cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS raw.{table_name} (
                        id SERIAL PRIMARY KEY,
                        data JSONB NOT NULL,
                        _extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """)

        # Clean old data
        cur.execute(f"""
            DELETE FROM raw.{table_name}
                WHERE _extracted_at < CURRENT_DATE - INTERVAL '2 days'
         """)

        # Insert data
        if isinstance(data, dict):
            for key, value in data.items():
                # Add key-value pair if not exists
                if isinstance(value, dict) and "id" not in value:
                    value["id"] = key

                cur.execute(
                    f"""
                        INSERT INTO raw.{table_name} (data)
                        VALUES (%s)
                            """,
                    (json.dumps(value),),
                )

        elif isinstance(data, list):
            for item in data:
                cur.execute(
                    f"""
                        INSERT INTO raw.{table_name} (data)
                        VALUES (%s)
                            """,
                    (json.dumps(item),),
                )

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise

    finally:
        if conn and cur:
            close_conn_cursor(conn, cur)
