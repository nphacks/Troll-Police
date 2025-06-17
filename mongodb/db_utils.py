from vertex_ai.categorize_comment import classify_comment
from pymongo import MongoClient
import datetime
from utils.embed_utils import get_embeddings
import os
from dotenv import load_dotenv

load_dotenv()

def get_data():
    # MongoDB logic here
    return "MongoDB data"

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]
videos_col = db["videos"]       
comments_col = db["comments"]
rules_col = db["rules"]

def test_mongo_connection():
    try:
        client = MongoClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=2000)
        client.server_info()  # Forces a call to test connection
        print("DB connected.")
    except Exception as e:
        print(f"DB connection failed: {e}")

def save_video_metadata(response):
    item = response["items"][0]["snippet"]
    video_doc = {
        "videoId": item["videoId"],
        "channelId": item["channelId"],
        "nextPageToken": response.get("nextPageToken"),
        "totalCommentCount": response["pageInfo"]["totalResults"],
        "timestamp": datetime.datetime.utcnow()
    }
    if not videos_col.find_one({"videoId": item["videoId"]}):
        videos_col.insert_one(video_doc)


def save_comments(response):
    comments = []
    texts = []

    for item in response["items"]:
        snippet = item["snippet"]["topLevelComment"]["snippet"]
        texts.append(snippet["textOriginal"])
        analysis = classify_comment(snippet["textDisplay"])
        category = analysis.label
        keywords = analysis.keywords
        sentiment = analysis.sentiment_score
        toxicity = analysis.toxicity_score
        comments.append({
            "videoId": snippet["videoId"],
            "commentId": item["snippet"]["topLevelComment"]["id"],
            "currentText": snippet["textDisplay"],
            "textOriginal": snippet["textOriginal"],
            "author": snippet["authorDisplayName"],
            "authorChannelUrl": snippet["authorChannelUrl"],
            "publishedAt": snippet["publishedAt"],
            "updatedAt": snippet["updatedAt"],
            "likeCount": snippet["likeCount"],
            "totalReplyCount": item["snippet"]["totalReplyCount"],
            "category": category,
            "keywords": keywords,
            "sentiment": sentiment,
            "toxicity": toxicity
        })

    embeddings = get_embeddings(texts)
    for i, comment in enumerate(comments):
        comment["embedding"] = embeddings[i]
        comment["timestamp"] = datetime.datetime.utcnow()

    if comments:
        comments_col.insert_many(comments)

    return comments

