from mongodb.db_utils import save_comments, save_video_metadata
from mongodb.video_comments_stats import get_video_comment_stats
from googleapiclient.discovery import build
import re
import os
import json
from dotenv import load_dotenv

load_dotenv()

def classify_text(text):
    # Vertex AI logic here
    return f"Classified: {text}"

def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
    return match.group(1) if match else None

def get_youtube_comments(video_url, max_comments=5):
    video_id = extract_video_id(video_url)
    if not video_id:
        return []

    youtube = build("youtube", "v3", developerKey=os.getenv("GOOGLE_API_KEY"))

    comments = []
    next_page_token = None
    first_page = True

    print('get youtube comments')

    while len(comments) < max_comments:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(100, max_comments - len(comments)),
            pageToken=next_page_token,
            textFormat="plainText"
        ).execute()

        with open("youtube_comments_response.json", "w", encoding="utf-8") as f:
            json.dump(response, f, ensure_ascii=False, indent=2)

        new_comments = save_comments(response)  # returns number of comments saved
        comments.extend(new_comments)

        if first_page:
            save_video_metadata(response)  # only once
            first_page = False

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    stats = get_video_comment_stats(video_id)

    return stats