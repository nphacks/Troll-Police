from flask import Flask, request, render_template
from mongodb.db_utils import get_data, test_mongo_connection
from mongodb.video_comments_stats import get_video_comment_stats  
from mongodb.sub_category_stats import get_subcategory_counts, check_subcategorization
from mongodb.fetch_all_videos import fetch_video_details  
from mongodb.fetch_comments import get_comments_by_category
from mongodb.similar_comments import find_similar_comments
from mongodb.keyword_stats import get_top_keywords  
from mongodb.comment_rules import upsert_rules, get_rules, check_rules
from mongodb.apply_rules import apply_rules
from mongodb.categories_subcategories import get_categories_and_subcategories
from vertex_ai.ai_utils import classify_text, get_youtube_comments  
from vertex_ai.summarize_comments import summarize_category_comments, summarize_subcategory_comments  
from utils.process_comments import subcategorize_comments
from dotenv import load_dotenv
from flask import jsonify
import json
from bson.json_util import dumps

load_dotenv()

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    videos = fetch_video_details()
    test_mongo_connection()
    test_mongo_connection()
    stats = None

    return render_template("index.html", stats=stats)
    # print('Total videos --->', len(videos))
        
    # if request.method == "POST":
    #     videoUrl = request.form.get("videoUrl", "")        
    #     stats = get_youtube_comments(videoUrl)  
    #     # videos = fetch_video_details()
    #     print(stats)
    #     return render_template("index.html", videos=videos, stats=stats)
    # else:
    #     return render_template("index.html", videos=videos, stats=None)

@app.route("/submit-url", methods=["POST"])
def submit_url():
    data = request.get_json()
    video_url = data.get("videoUrl", "")
    stats = get_youtube_comments(video_url)
    return jsonify(stats)


@app.route("/videos")
def videos():
    videos = fetch_video_details()
    return jsonify(videos)


# @app.route("/get-all-videos", methods=["GET"])
# def get_all_videos():
#     if request.method == "GET":
#         videos = fetch_video_details()
#         print(videos)
#         return f"Stats: {videos}" 

@app.route("/category-stats", methods=["GET"])
def category_stats():
    video_id = request.args.get("videoId")
    stats = get_video_comment_stats(video_id)
    return jsonify(stats)
    # if request.method == "GET":
    #     videoId='Ca4nR6IRJ88'
    #     stats = get_video_comment_stats(videoId)
    #     print(stats)
    #     return f"Stats: {stats}" 
    
@app.route("/subcategorize", methods=["POST"])
def subcategorize():
    video_id = request.form.get("videoId")
    if not video_id:
        return jsonify({"code": 404, "message": "No video found"})

    success = subcategorize_comments(video_id)
    if success:
        return jsonify({"code": 200, "message": "Sub Categorization done!"})
    return jsonify({"code": 404, "message": f"Video ID {video_id} not found."})
    
@app.route("/sub-category-stats", methods=["GET"])
def sub_category_stats():
    videoId = request.args.get("videoId")
    stats = get_subcategory_counts(videoId)
    return jsonify(stats)

@app.route("/check-subcategory", methods=["GET"])
def check_video_subcategory():
    videoId = request.args.get("videoId")
    subCategoryBool = check_subcategorization(videoId)
    return jsonify(subCategoryBool)

@app.route("/keyword-stats", methods=["GET"])
def keyword_stats():
    videoId = request.args.get("videoId")
    stats = get_top_keywords(videoId)
    return jsonify(stats)

@app.route("/get-categories-subcategories", methods=["GET"])
def get_categories_subcategories():
    if request.method == "GET":
        videoId = request.args.get("videoId")
        cat_subcat = get_categories_and_subcategories(videoId)
        return jsonify(cat_subcat)
    
@app.route("/get-comments", methods=["GET"])
def get_comments():
    if request.method == "GET":
        videoId = request.args.get("videoId")
        category = request.args.get("category")
        subcategory = request.args.get("subcategory")
        comments = get_comments_by_category(videoId, category, subcategory)
        return jsonify(comments)
    
@app.route("/get-similar-comments", methods=["GET"])
def get_similar_comments():
    if request.method == "GET":
        commentId='UgwGJOTYouk2q99Y2IB4AaABAg'
        comments = find_similar_comments(commentId, 10)
        print(comments)
        return f"Comments: {comments}" 
    
@app.route("/create-rules", methods=["POST"])
def create_video_rules():
    video_id = request.form.get("videoId")
    if not video_id:
        return jsonify({"code": 400, "message": "Missing videoId"})

    categories = json.loads(request.form.get("categories", "[]"))
    subcategories = json.loads(request.form.get("subcategories", "[]"))
    keywords = json.loads(request.form.get("keywords", "[]"))
    phrases = json.loads(request.form.get("phrases", "[]"))

    success = upsert_rules(video_id, categories, subcategories, keywords, phrases)
    if success:
        return jsonify({"code": 200, "message": "Rules created successfully!"})
    return jsonify({"code": 404, "message": f"Rule {video_id} not created."})

@app.route("/get-video-rules", methods=["GET"])
def get_video_rules():
    videoId = request.args.get("videoId")
    rules = get_rules(videoId)
    return dumps(rules), 200, {'Content-Type': 'application/json'}

@app.route("/check-rules", methods=["GET"])
def check_video_rules():
    videoId = request.args.get("videoId")
    rulesBool = check_rules(videoId)
    return jsonify(rulesBool)
    
@app.route("/apply-rules", methods=["GET"])
def apply_video_rules():
    if request.method == "GET":
        videoId = request.args.get("videoId")
        apply_rules(videoId)
        return jsonify({"code": 200, "message": "Rules applied!"})

@app.route("/summarize-comments", methods=["GET"])
def summary_category_comments():
    videoId = request.args.get("videoId")
    category = request.args.get("category")
    subcategory = request.args.get("subcategory")

    category_summary = summarize_category_comments(videoId, category) if category else ""
    subcategory_summary = summarize_subcategory_comments(videoId, subcategory) if subcategory else ""
    
    return jsonify({
        "category_summary": category_summary,
        "subcategory_summary": subcategory_summary
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)