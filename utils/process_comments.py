from vertex_ai.subcategorize_comment import generate_subcategory
from scipy.spatial.distance import cosine
import numpy as np
from datetime import datetime
from mongodb.db_utils import videos_col, comments_col
from sklearn.cluster import AgglomerativeClustering

def cosine_similarity(v1, v2):
    return 1 - cosine(v1, v2)

def normalize(v):
    v = np.array(v)
    return (v / np.linalg.norm(v)).tolist()

def update_avg_embedding(old_avg, new_emb, n):
    return ((np.array(old_avg) * n + np.array(new_emb)) / (n + 1)).tolist()

def cluster_subcategories(subcat_meta, threshold=0.3):
    if len(subcat_meta) < 2:
        return subcat_meta

    embeddings = [normalize(sc["avgEmbedding"]) for sc in subcat_meta]
    labels = AgglomerativeClustering(
        n_clusters=None, distance_threshold=threshold, metric='cosine', linkage='average'
    ).fit(embeddings).labels_

    clustered = {}
    for idx, label in enumerate(labels):
        key = f"group_{label}"
        sc = subcat_meta[idx]
        if key not in clustered:
            clustered[key] = {
                "subcategory": sc["subcategory"],
                "count": sc["count"],
                "avgEmbedding": np.array(sc["avgEmbedding"]) * sc["count"],
            }
        else:
            clustered[key]["count"] += sc["count"]
            clustered[key]["avgEmbedding"] += np.array(sc["avgEmbedding"]) * sc["count"]

    result = []
    for item in clustered.values():
        result.append({
            "subcategory": item["subcategory"],
            "count": item["count"],
            "avgEmbedding": (item["avgEmbedding"] / item["count"]).tolist(),
            "threshold": 0.7
        })
    return result

def subcategorize_comments(video_id):
    video = videos_col.find_one({"videoId": video_id})
    if not video: return False

    comments = list(comments_col.find({"videoId": video_id}))
    subcat_meta = video.get("subCategoryMetadata", [])

    print('Total comments', len(comments))

    for c in comments:
        main_cat = c.get("category")
        emb = normalize(c["embedding"])
        matched = False

        for sc in subcat_meta:
            sc_emb = normalize(sc["avgEmbedding"])
            if cosine_similarity(emb, sc_emb) >= sc.get("threshold", 0.7):
                sc["count"] += 1
                sc["avgEmbedding"] = update_avg_embedding(sc["avgEmbedding"], emb, sc["count"] - 1)
                c_sub = sc["subcategory"]
                matched = True
                break

        if not matched:
            new_label = generate_subcategory(c["textOriginal"], main_cat)
            subcat_meta.append({
                "subcategory": new_label,
                "count": 1,
                "avgEmbedding": emb,
                "threshold": 0.7
            })
            c_sub = new_label

        comments_col.update_one({"_id": c["_id"]}, {"$set": {"subCategory": c_sub}})

    subcat_meta = cluster_subcategories(subcat_meta)

    videos_col.update_one({"videoId": video_id}, {
        "$set": {
            "subCategoryMetadata": subcat_meta,
            "updatedAt": datetime.utcnow()
        }
    })

    return True
