from mongodb.db_utils import client
import os
from dotenv import load_dotenv

load_dotenv() 

def get_video_comment_stats(video_id):
    pipeline = [
        {"$match": {"videoId": video_id}},
        {
            "$group": {
                "_id": "$category",
                "count": {"$sum": 1},
                "avg_sentiment": {"$avg": "$sentiment"},
                "avg_toxicity": {"$avg": "$toxicity"}
            }
        }
    ]

    db = client[os.getenv("MONGO_DB")]
    raw_result = list(db.comments.aggregate(pipeline))

    result = []
    for item in raw_result:
        result.append({
            "category": item["_id"],
            "count": item["count"],
            "avg_sentiment": round(item["avg_sentiment"], 2),
            "avg_toxicity": round(item["avg_toxicity"], 2)
        })

    total_sentiment = sum(item["avg_sentiment"] * item["count"] for item in raw_result)
    total_toxicity = sum(item["avg_toxicity"] * item["count"] for item in raw_result)
    total_count = sum(item["count"] for item in raw_result)

    result.append({
        "category": "All",
        "count": total_count,
        "avg_sentiment": round(total_sentiment / total_count, 2),
        "avg_toxicity": round(total_toxicity / total_count, 2)
    })
    result.append({"videoId": video_id})

    return result
