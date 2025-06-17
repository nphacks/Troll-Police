from googleapiclient.discovery import build
from mongodb.db_utils import client
import os
from dotenv import load_dotenv

load_dotenv() 

def fetch_video_details():
    db = client[os.getenv("MONGO_DB")]
    video_ids = db.videos.distinct("videoId")

    youtube = build("youtube", "v3", developerKey=os.getenv("GOOGLE_API_KEY"))
    details = []

    for vid in video_ids:
        response = youtube.videos().list(
            part="snippet,statistics",
            id=vid
        ).execute()

        if response["items"]:
            item = response["items"][0]
            details.append({
                "videoId": vid,
                "title": item["snippet"]["title"],
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                "total_comments": int(item["statistics"].get("commentCount", 0))
            })

    return details
