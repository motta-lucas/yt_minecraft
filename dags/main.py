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
    get_channel_stats,
    get_playlist_id,
    get_videos_ids,
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
    dag_id="produce_videos_json",
    default_args=default_args,
    description="DAG to produce JSON file with raw data",
    schedule="0 14 * * *",
    catchup=False,
    tags=["yt", "ingest", "videos"],
) as dag_produce:

    @task
    def playlist_ids():
        api_key = Variable.get("YT_API_KEY")
        channel_handle = json.loads(Variable.get("CHANNEL_HANDLE"))
        return [get_playlist_id(item, api_key) for item in channel_handle]

    @task
    def videos_ids(playlist_id_list):
        api_key = Variable.get("YT_API_KEY")
        max_results = 50

        ids = []
        for playlist_id in playlist_id_list:
            ids += get_videos_ids(max_results, playlist_id, api_key)
        return ids

    @task
    def extract_data(video_ids):
        api_key = Variable.get("YT_API_KEY")
        max_results = 50
        return extract_video_data(video_ids, api_key, max_results)

    @task
    def save_and_load_videos(extracted_data, data_origin: str = "videos_data"):
        airflow_home = Path(os.getenv("AIRFLOW_HOME", "/opt/airflow"))
        data_dir = airflow_home / "data" / data_origin
        data_dir.mkdir(parents=True, exist_ok=True)

        postgres_conn_id = "postgres_db_yt_elt"
        db_name = os.environ["ELT_DATABASE_NAME"]

        save_to_minio(extracted_data, data_origin)

        conn, cur = get_conn_cursor(postgres_conn_id, db_name)
        try:
            load_json_to_postgres(cur, conn, extracted_data, data_origin)
            save_to_json(extracted_data, data_dir)
        finally:
            close_conn_cursor(conn, cur)

    p = playlist_ids()
    v = videos_ids(p)
    d = extract_data(v)
    s = save_and_load_videos(d)

    trigger_produce_channel_json = TriggerDagRunOperator(
        task_id="trigger_produce_channel_json",
        trigger_dag_id="produce_channel_json",
    )

    p >> v >> d >> s >> trigger_produce_channel_json

with DAG(
    dag_id="produce_channel_json",
    default_args=default_args,
    description="DAG to produce JSON file with raw data",
    schedule=None,
    catchup=False,
    tags=["yt", "ingest", "channel"],
) as dag_produce:

    @task
    def channel_stats():
        api_key = Variable.get("YT_API_KEY")
        channel_handle = json.loads(Variable.get("CHANNEL_HANDLE"))
        return [get_channel_stats(item, api_key) for item in channel_handle]

    @task
    def save_and_load_channel(extracted_data, data_origin: str = "channels_data"):
        airflow_home = Path(os.getenv("AIRFLOW_HOME", "/opt/airflow"))
        data_dir = airflow_home / "data" / data_origin
        data_dir.mkdir(parents=True, exist_ok=True)

        postgres_conn_id = "postgres_db_yt_elt"
        db_name = os.environ["ELT_DATABASE_NAME"]

        # Saves json to MinIO service, meant to substitute local saving
        save_to_minio(extracted_data, data_origin)

        conn, cur = get_conn_cursor(postgres_conn_id, db_name)
        try:
            load_json_to_postgres(cur, conn, extracted_data, data_origin)
            save_to_json(extracted_data, data_dir)
        finally:
            close_conn_cursor(conn, cur)

    channel_stats_task = channel_stats()
    save_channel_data_task = save_and_load_channel(channel_stats_task)

    trigger_dbt = TriggerDagRunOperator(
        task_id="trigger_dbt_pipeline",
        trigger_dag_id="dbt_youtube_pipeline",
        wait_for_completion=True,
        poke_interval=30,
    )

    channel_stats_task >> save_channel_data_task >> trigger_dbt
