from pymongo import UpdateOne
from bson import ObjectId
from datetime import datetime
from mongodb.db_utils import client
import os
from dotenv import load_dotenv

load_dotenv() 

db = client[os.getenv("MONGO_DB")]
rules_col = db.rules

# Functions to get, check existence, and upsert (insert or update) rules by video ID.

def get_rules(video_id):
    rule = rules_col.find_one({"videoId": video_id})
    if not rule:
        return []
    return rule

def check_rules(video_id):
    rule = rules_col.find_one({"videoId": video_id})
    if not rule:
        return False
    return True

# Manages content moderation rules in MongoDB for each video.
# Supports fields like notAllowedWords, blockCategories, blockSubCategories, and contentRules.
# Uses timestamps for createdAt and updatedAt to track rule changes.
def upsert_rules(video_id, block_categories=None, block_subcategories=None, not_allowed_words=None,  content_rules=None):
    # print(not_allowed_words, block_categories, block_subcategories, content_rules)
    now = datetime.utcnow()
    update_fields = {"updatedAt": now}

    if not_allowed_words is not None:
        update_fields["notAllowedWords"] = not_allowed_words
    if block_categories is not None:
        update_fields["blockCategories"] = block_categories
    if block_subcategories is not None:
        update_fields["blockSubCategories"] = block_subcategories
    if content_rules is not None:
        update_fields["contentRules"] = content_rules

    rules_col.update_one(
        {"videoId": video_id},
        {
            "$setOnInsert": {
                "createdAt": now
            },
            "$set": update_fields
        },
        upsert=True
    )

    return True

