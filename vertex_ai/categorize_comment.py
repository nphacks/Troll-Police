from google import genai
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

# This script uses Gemini AI to analyze YouTube comments.
# It classifies comments into predefined categories, extracts keywords, and computes sentiment and toxicity scores.
# The classification is structured using a Pydantic model for validation.

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

LABELS = ["Positive", "Negative", "Spam", "Question", "Feedback", "Promotional"]

label_definitions = {
    "Positive": "Expresses approval, happiness, excitement, or praise.",
    "Negative": "Expresses criticism, disappointment, anger, or dislike.",
    "Spam": "Irrelevant or repetitive comment not contributing to the discussion, often containing links or generic text.",
    "Question": "Asks for information, clarification, or opinion.",
    "Feedback": "Provides constructive suggestions or opinions to improve content.",
    "Promotional": "Tries to sell, advertise, or promote a product, service, or channel."
}

class CommentAnalysis(BaseModel):
    label: str
    keywords: list[str]
    sentiment_score: float  
    toxicity_score: float  

# model = genai.GenerativeModel("gemini-2.0-flash")

def classify_comment(text):    
    prompt = (
        f"Analyze the following YouTube comment.\n"
        f"Label the comment into one of the following categories:\n"
        + "\n".join([f"- {label}: {definition}" for label, definition in label_definitions.items()]) +
        f"\n\nReturn:\n"
        f"- label: One of the above\n"
        f"- keywords: List of important keywords in the comment\n"
        f"- sentiment_score: -1 (very negative) to 1 (very positive)\n"
        f"- toxicity_score: 0 (not toxic) to 1 (very toxic)\n\n"
        f"Comment: \"{text}\""
    )

    # response = model.generate_content(
    #     prompt,
    #     generation_config={"response_mime_type": "application/json"},
    #     safety_settings=None,
    #     response_schema=CommentAnalysis
    # )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": CommentAnalysis,
        },
    )


    return response.parsed