from pymongo import UpdateOne
from bson import ObjectId
from datetime import datetime
from mongodb.db_utils import client
import os
from dotenv import load_dotenv

load_dotenv() 

db = client[os.getenv("MONGO_DB")]
rules_col = db.rules


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

def upsert_rules(video_id, not_allowed_words=None, block_categories=None, block_subcategories=None, content_rules=None):
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

