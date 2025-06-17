from mongodb.db_utils import client, videos_col
import os
from dotenv import load_dotenv

load_dotenv() 

def get_subcategory_counts(video_id):
    pipeline = [
        {"$match": {"videoId": video_id}},
        {
            "$group": {
                "_id": {"category": "$category", "subCategory": "$subCategory"},
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id.category": 1, "count": -1}},  
        {
            "$group": {
                "_id": "$_id.category",
                "subcategories": {
                    "$push": {
                        "subCategory": "$_id.subCategory",
                        "count": "$count"
                    }
                }
            }
        },
        {"$project": {"_id": 0, "category": "$_id", "subcategories": 1}}
    ]

    db = client[os.getenv("MONGO_DB")]
    result = list(db.comments.aggregate(pipeline))
    return result

def check_subcategorization(video_id):
    video = videos_col.find_one({"videoId": video_id})
    return "subCategoryMetadata" in video if video else False