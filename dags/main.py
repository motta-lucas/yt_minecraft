import json
import os
from pathlib import Path
from datetime import datetime, timedelta

import pendulum
from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable

from yt_minecraft.airflow.postgres import get_conn_cursor, close_conn_cursor
from yt_minecraft.api.youtube import get_playlist_id, get_videos_ids, extract_video_data, save_to_json
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
    dag_id="produce_json",
    default_args=default_args,
    description="DAG to produce JSON file with raw data",
    schedule="0 14 * * *",
    catchup=False,
    tags=["yt", "ingest"],
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
    def save_and_load(extracted_data, data_origin: str = "videos_data"):
        airflow_home = Path(os.getenv("AIRFLOW_HOME", "/opt/airflow"))
        data_dir = airflow_home / "data" / data_origin
        data_dir.mkdir(parents=True, exist_ok=True)

        postgres_conn_id = "postgres_db_yt_elt"
        db_name = os.environ["ELT_DATABASE_NAME"]

        conn, cur = get_conn_cursor(postgres_conn_id, db_name)
        try:
            load_json_to_postgres(cur, conn, extracted_data, data_origin)
            save_to_json(extracted_data, data_dir)
        finally:
            close_conn_cursor(conn, cur)

    p = playlist_ids()
    v = videos_ids(p)
    d = extract_data(v)
    s = save_and_load(d)

    p >> v >> d >> s
