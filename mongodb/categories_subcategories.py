from mongodb.db_utils import client
import os
from dotenv import load_dotenv

load_dotenv()

# Retrieves unique categories and subcategories from comments of a specific video in MongoDB.
# Queries comments collection filtering by video ID, extracts distinct category and subCategory values.
# Returns a dictionary with lists of unique categories and subcategories found.
def get_categories_and_subcategories(video_id):
    db = client[os.getenv("MONGO_DB")]
    comments = db.comments.find({"videoId": video_id}, {"category": 1, "subCategory": 1, "_id": 0})

    categories = set()
    subcategories = set()

    for comment in comments:
        if "category" in comment and comment["category"]:
            categories.add(comment["category"])
        if "subCategory" in comment and comment["subCategory"]:
            subcategories.add(comment["subCategory"])

    return {
        "categories": list(categories),
        "subcategories": list(subcategories)
    }
