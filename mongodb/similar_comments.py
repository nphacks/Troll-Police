from mongodb.db_utils import client
import os
from dotenv import load_dotenv

load_dotenv() 

def find_similar_comments(comment_id, top_k=5):
    db = client[os.getenv("MONGO_DB")]
    comment = db.comments.find_one({"commentId": comment_id})
    print(db.comments.index_information())
    if not comment or "embedding" not in comment:
        return []

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": comment["embedding"],
                "numCandidates": 100,
                "limit": top_k + 1, 
                "similarity": "cosine"
            }
        },
        {
            "$match": {
                "_id": {"$ne": comment_id}
            }
        },
        {
            "$project": {
                "_id": 0,
                "textOriginal": 1,
            }
        }
    ]

    return list(db.comments.aggregate(pipeline))
