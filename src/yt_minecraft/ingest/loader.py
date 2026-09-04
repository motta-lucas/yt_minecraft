import json
from typing import Any, Dict

from yt_minecraft.db.postgres import create_schema
from yt_minecraft.db.raw_schema import ensure_raw_table


def load_json_to_postgres(cur, conn, data, data_origin):

    table_mapping = {
        "videos_data": ("videos_data_json", "video_id"),
        "channels_data": ("channels_data_json", "channel_id"),
    }

    table_name, key_column = table_mapping.get(data_origin, (f"{data_origin}_json", "id"))

    create_schema(cur, "raw")

    ensure_raw_table(cur, table_name, key_column)

    def insert_item(item: dict):
        vid = item.get(key_column) or item.get("id")
        cur.execute(
            f"INSERT INTO raw.{table_name} ({key_column},data) VALUES (%s, %s)", (vid, json.dumps(item))
        )

    # Clean old data
    cur.execute(f"""
        DELETE FROM raw.{table_name}
            WHERE _extracted_at < CURRENT_DATE - INTERVAL '7 days'
        """)

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
