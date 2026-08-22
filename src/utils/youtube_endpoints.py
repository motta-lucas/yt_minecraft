import requests
from datetime import date
import json
from pathlib import Path


def get_playlist_id(channel_handle, api_key):
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={channel_handle}&key={api_key}"

        response = requests.get(url)

        response.raise_for_status()

        data = response.json()

        channel_playlistID = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

        print(channel_playlistID)

        return channel_playlistID

    except requests.exceptions.RequestException as e:
        raise e


def get_videos_ids(maxResults, playlistID, api_key):

    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlistID}&key={api_key}"
    video_ids = []

    pageToken = None

    try:
        while True:

            url = base_url

            if pageToken:
                url += f"&pageToken={pageToken}"

            response = requests.get(url)

            response.raise_for_status()

            data = response.json()

            for item in data.get("items", []):
                video_id = item["contentDetails"]["videoId"]
                video_ids.append(video_id)

            pageToken = data.get("nextPageToken")

            if not pageToken:
                break

        return video_ids

    except requests.exceptions.RequestException as e:
        raise e


def extract_video_data(video_ids, api_key, maxResults):

    extracted_data = []

    def batch_list(video_id_list, batch_size):
        for video_id in range(0, len(video_id_list), batch_size):
            yield video_id_list[video_id : video_id + batch_size]

    try:
        for batch in batch_list(video_ids, maxResults):
            video_ids_str = ",".join(batch)

            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={api_key}"

            response = requests.get(url)

            response.raise_for_status()

            data = response.json()

            for item in data.get("items", []):
                video_id = item["id"]
                snippet = item["snippet"]
                contentDetails = item["contentDetails"]
                statistics = item["statistics"]

                video_data = {
                    "video_id": video_id,
                    "title": snippet["title"],
                    "publishedAt": snippet["publishedAt"],
                    "duration": contentDetails["duration"],
                    "viewCount": statistics.get("viewCount", None),
                    "likeCount": statistics.get("likeCount", None),
                    "commentCount": statistics.get("commentCount", None),
                    "channelTitle": snippet["channelTitle"],
                    "channelId": snippet["channelId"],
                }

                extracted_data.append(video_data)

        return extracted_data
    except requests.exceptions.RequestException as e:
        raise e


def save_to_json(extracted_data, output_dir):
    file_path = Path(output_dir) / f"yt_data_{date.today()}.json"

    with open(file_path, "w", encoding="utf-8") as json_outfile:
        json.dump(extracted_data, json_outfile, indent=4, ensure_ascii=False)
