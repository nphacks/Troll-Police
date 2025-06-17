from datetime import datetime
from mongodb.db_utils import comments_col, rules_col
from vertex_ai.rule_checker import violates_content_rules

def apply_rules(video_id):
    rules = rules_col.find_one({"videoId": video_id})
    if not rules:
        return False

    block_categories = set(rules.get("blockCategories", []))
    block_subcategories = set(rules.get("blockSubCategories", []))
    not_allowed_words = set(word.lower() for word in rules.get("notAllowedWords", []))
    content_rules = rules.get("contentRules", [])

    comments = list(comments_col.find({"videoId": video_id}))

    for c in comments:
        reasons = []
        text = c.get("currentText", "").lower()
        category = c.get("category")
        subcategory = c.get("subCategory")

        if category in block_categories:
            reasons.append(f"Blocked category: {category}")
        if subcategory in block_subcategories:
            reasons.append(f"Blocked sub-category: {subcategory}")
        if any(word in text for word in not_allowed_words):
            reasons.append("Contains not allowed words")
        violated_reasons = violates_content_rules(text, content_rules)
        if content_rules:
            violated_reasons = violates_content_rules(text, content_rules)
            if violated_reasons:
                reasons.extend([f"Violates rule: {r}" for r in violated_reasons])


        comments_col.update_one(
            {"_id": c["_id"]},
            {
                "$set": {
                    "display": len(reasons) == 0,
                    "displayReasons": reasons,
                    "updatedAt": datetime.utcnow()
                }
            }
        )

    return True
