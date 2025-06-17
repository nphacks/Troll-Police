from mongodb.db_utils import client
import os
from dotenv import load_dotenv

load_dotenv() 

# Retrieves comments for a specific video filtered optionally by category and/or subcategory.
# Returns detailed comment fields including text, categories, display status, likes, replies, sentiment, and toxicity.

# Retrieves only comments marked as displayable (display=True) for a video, 
# optionally filtered by category and/or subcategory.
# Returns limited fields: original text, category, and subcategory.

def get_comments_by_category(video_id, category=None, subcategory=None):
    query = {"videoId": video_id}
    
    if category:
        query["category"] = category
    if subcategory:
        query["subCategory"] = subcategory

    db = client[os.getenv("MONGO_DB")]
    comments = list(db.comments.find(query, {
        "_id": 0, 
        "textOriginal": 1, 
        "category": 1, 
        "subCategory": 1, 
        "display": 1, 
        "displayReasons": 1, 
        "likeCount": 1, 
        "updatedAt": 1, 
        "totalReplyCount": 1, 
        "sentiment": 1, 
        "toxicity": 1
    }))
    return comments

def get_display_comments(video_id, category=None, subcategory=None):
    query = {"videoId": video_id, "display": True}
    
    if category:
        query["category"] = category
    if subcategory:
        query["subCategory"] = subcategory

    db = client[os.getenv("MONGO_DB")]
    comments = list(db.comments.find(query, {"_id": 0, "textOriginal": 1, "category": 1, "subCategory": 1}))
    return comments