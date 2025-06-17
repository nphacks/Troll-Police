from mongodb.db_utils import client
import os
from dotenv import load_dotenv

# Aggregates and returns the top N most frequent keywords from comments of a given video.
# Uses MongoDB aggregation to count occurrences of each keyword across all comments for the video.
# Returns a list of dictionaries with 'keyword' and its 'count', sorted by frequency descending.

load_dotenv() 

def get_top_keywords(video_id, n=20):
    pipeline = [
        {"$match": {"videoId": video_id}},
        {"$unwind": "$keywords"},
        {
            "$group": {
                "_id": "$keywords",
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": n},
        {
            "$project": {
                "_id": 0,
                "keyword": "$_id",
                "count": 1
            }
        }
    ]

    db = client[os.getenv("MONGO_DB")]
    result = list(db.comments.aggregate(pipeline))
    return result
