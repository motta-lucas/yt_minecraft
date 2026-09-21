import json
import os
from pathlib import Path
from datetime import datetime, timedelta

import pendulum
from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from yt_minecraft.airflow.postgres import get_conn_cursor, close_conn_cursor
from yt_minecraft.api.youtube import (
    get_recent_videos,
    extract_video_data,
    save_to_json,
)

from yt_minecraft.storage.minio import save_to_minio
from yt_minecraft.ingest.loader import load_json_to_postgres

local_tz = pendulum.timezone("America/Sao_Paulo")

default_args = {
    "owner": "motta-lucas",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "lmottta.ds@gmail.com",
    "max_active_runs": 1,
    "dagrun_timeout": timedelta(hours=1),
    "start_date": datetime(2025, 1, 1, tzinfo=local_tz),
}

with DAG(
    dag_id="produce_recent_videos_json",
    default_args=default_args,
    description="DAG to produce JSON file with raw data",
    schedule="0 */2 * * *",
    catchup=False,
    tags=["yt", "ingest", "videos"],
) as dag_produce:

    @task
    def recent_ids():
        postgres_conn_id = "postgres_db_yt_elt"
        db_name = os.environ["ELT_DATABASE_NAME"]

        conn, cur = get_conn_cursor(postgres_conn_id, db_name)
        try:
            ids = get_recent_videos(cur, "staging_dbt", "stg_youtube_videos")
        finally:
            close_conn_cursor(conn, cur)
        return ids

    @task
    def extract_data(video_ids):
        api_key = Variable.get("YT_API_KEY")
        max_results = 50
        return extract_video_data(video_ids, api_key, max_results)

    @task
    def save_and_load_videos(extracted_data, data_origin: str = "recent_videos_data"):
        airflow_home = Path(os.getenv("AIRFLOW_HOME", "/opt/airflow"))
        data_dir = airflow_home / "data" / data_origin
        data_dir.mkdir(parents=True, exist_ok=True)

        postgres_conn_id = "postgres_db_yt_elt"
        db_name = os.environ["ELT_DATABASE_NAME"]

        save_to_minio(extracted_data, data_origin)

        conn, cur = get_conn_cursor(postgres_conn_id, db_name)
        try:
            # load_json_to_postgres(cur, conn, extracted_data, data_origin)
            save_to_json(extracted_data, data_dir, timestamped=True)
        finally:
            close_conn_cursor(conn, cur)

    r = recent_ids()
    d = extract_data(r)
    s = save_and_load_videos(d)

    r >> d >> s
