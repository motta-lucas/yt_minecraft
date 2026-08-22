from airflow import DAG
import pendulum
from datetime import datetime, timedelta
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from api.youtube_channels_data import (
    dag_playlist_id,
    dag_videos_ids,
    dag_extract_video_data,
    dag_save_to_json,
)

# from datawarehouse.dwh import staging_table, core_table

# from dataquality.soda import yt_elt_data_quality

# define the local timezone
local_tz = pendulum.timezone("America/Sao_Paulo")

default_args = {
    "owner": "motta-lucas",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "lmotta.ds@gmail.com",
    # 'retries': 1,
    # 'retry_delay': timedelta(minutes=5),
    "max_active_runs": 1,
    "dagrun_timeout": timedelta(hours=1),
    "start_date": datetime(2025, 1, 1, tzinfo=local_tz),
    # 'end_date': datetime(2030,12,31,tzinfo=local_tz)
}

staging_schema = "staging"
core_schema = "core"

with DAG(
    dag_id="produce_json",
    default_args=default_args,
    description="DAG to produce JSON file with raw data",
    schedule="0 14 * * *",
    catchup=False,
) as dag_produce:

    # Define tasks
    playlist_id = dag_playlist_id()
    video_ids = dag_videos_ids(playlist_id)
    extract_data = dag_extract_video_data(video_ids)
    save_to_json_task = dag_save_to_json(extract_data)

    trigger_update_db = TriggerDagRunOperator(
        task_id="trigger_update_db",
        trigger_dag_id="update_db",
    )

    # Define dependencies

    playlist_id >> video_ids >> extract_data >> save_to_json_task
