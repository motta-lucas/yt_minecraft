import requests
import json
from datetime import date


from utils.youtube_endpoints import get_playlist_id, get_videos_ids, extract_video_data, save_to_json
from utils.log_config import logs_config

from pathlib import Path


from airflow.decorators import task
from airflow.models import Variable

API_KEY = Variable.get("YT_API_KEY")
CHANNEL_HANDLE = Variable.get("CHANNEL_HANDLE")
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
def dag_save_to_json(extracted_data):
    DATA_DIR = Path.cwd().parent / "data"

    save_to_json(extracted_data, DATA_DIR)


if __name__ == "__main__":
    playlistID = dag_playlist_id()
    video_ids = dag_videos_ids(playlistID)
    video_data = dag_extract_video_data(video_ids)
    dag_save_to_json(video_data)
else:
    print("dag_playlist_id won't be executed")
