import json
from typing import Any, Dict

from yt_minecraft.db.postgres import create_schema
from yt_minecraft.db.raw_schema import ensure_raw_table


def load_json_to_postgres(cur, conn, data, data_origin):

    table_mapping = {
        "yt_data": "videos_data_json",
    }

    table_name = table_mapping.get(data_origin, f"{data_origin}_json")

    create_schema(cur, "raw")

    ensure_raw_table(cur, table_name)

    def insert_item(item: dict):
        vid = item.get("video_id") or item.get("id")
        cur.execute(f"INSERT INTO raw.{table_name} (video_id,data) VALUES (%s, %s)", (vid, json.dumps(item)))

    # Insert data
    if isinstance(data, dict):
        for key, value in data.items():
            # Add key-value pair if not exists
            if isinstance(value, dict) and "id" not in value:
                value["id"] = key
            if isinstance(value, dict):
                insert_item(value)

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                insert_item(item)

    conn.commit()
