from vertex_ai.categorize_comment import client
from mongodb.db_utils import comments_col
from datetime import datetime

# Functions to summarize comments by category or subcategory for a given video.
# Fetches relevant comments from MongoDB, compiles their texts, and prompts Gemini AI to generate a concise summary paragraph.
# Returns a well-written summary capturing main opinions without emojis.
# Handles cases where no comments are found by returning an informative message.

def summarize_category_comments(video_id, category):
    comments = list(comments_col.find(
        {"videoId": video_id, "category": category},
        {"textOriginal": 1}
    ))
    texts = [c["textOriginal"] for c in comments]

    if not texts:
        return f"No displayable comments for category: {category}"

    prompt = (
        f"Summarize the following YouTube comments that belong to the category '{category}'.\n"
        f"Capture the main opinions in a paragraph. No emojis. Write proper language.\n\n"
        + "\n".join([f"- {t}" for t in texts])
    )

    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response.text


def summarize_subcategory_comments(video_id, subcategory):
    comments = list(comments_col.find(
        {"videoId": video_id, "subCategory": subcategory},
        {"textOriginal": 1}
    ))
    texts = [c["textOriginal"] for c in comments]

    if not texts:
        return f"No displayable comments for sub-category: {subcategory}"

    prompt = (
        f"Summarize the following YouTube comments that belong to the sub-category '{subcategory}'.\n"
        f"Capture the main opinions in a paragraph. No emojis. Write proper language.\n\n"
        + "\n".join([f"- {t}" for t in texts])
    )

    response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
    return response.text
