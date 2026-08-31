import json
import os


from api.youtube_channels_endpoint import get_playlist_id, get_videos_ids, extract_video_data, save_to_json
from api.data_utils import load_json_to_postgres
from utils.log_config import logs_config

from pathlib import Path

from airflow.decorators import task
from airflow.models import Variable

API_KEY = Variable.get("YT_API_KEY")
CHANNEL_HANDLE_STR = Variable.get("CHANNEL_HANDLE")

CHANNEL_HANDLE = json.loads(CHANNEL_HANDLE_STR)

maxResults = 50


@task
def dag_playlist_id():
    playlist_id = []

    for item in CHANNEL_HANDLE:

        playlist_id.append(get_playlist_id(item, API_KEY))

    return playlist_id


@task
def dag_videos_ids(playlistID):

    videos_ids = []

    for item in playlistID:
        videos_ids = videos_ids + get_videos_ids(maxResults, item, API_KEY)

    return videos_ids


@task
def dag_extract_video_data(videos_ids):

    return extract_video_data(videos_ids, API_KEY, maxResults)


@task
def dag_save_to_json(data_origin, extracted_data):
    AIRFLOW_HOME = Path(os.getenv("AIRFLOW_HOME", "/opt/airflow"))

    DATA_DIR = AIRFLOW_HOME / "data" / f"{data_origin}"

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    load_json_to_postgres(extracted_data, data_origin)

    save_to_json(extracted_data, DATA_DIR)


if __name__ == "__main__":
    playlistID = dag_playlist_id()
    video_ids = dag_videos_ids(playlistID)
    video_data = dag_extract_video_data(video_ids)
    dag_save_to_json("videos_data", video_data)
else:
    print("dag_playlist_id won't be executed")
