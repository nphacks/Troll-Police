from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
import numpy as np
from scipy.spatial.distance import cosine
from datetime import datetime
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Flask app helper function that uses Gemini AI to generate a concise subcategory label for a comment.
# Provides the model with category context and examples to produce a 5-6 word descriptive subcategory.
# Ensures subcategories are general and avoid specific names.
# Returns the generated subcategory string.


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

label_definitions = {
    "Positive": "Expresses approval, happiness, excitement, or praise.",
    "Negative": "Expresses criticism, disappointment, anger, or dislike.",
    "Spam": "Irrelevant or repetitive comment not contributing to the discussion, often containing links or generic text.",
    "Question": "Asks for information, clarification, or opinion.",
    "Feedback": "Provides constructive suggestions or opinions to improve content.",
    "Promotional": "Tries to sell, advertise, or promote a product, service, or channel."
}

def generate_subcategory(text, category):
    # prompt = (
    #     f"Generate a sub-category for the given comment."
    #     f"Try to use 5 words or at max 8."
    #     f"Follow the format of <Tone/Emotion> <Focus/Intent> <Topic/Target"
    #     f"Describe the comment. For understanding: "
    #     f"If the comment is appreciating something then categorize 'Appreciating the <whatever is appreciated>'."
    #     f"If it is a racist, sexist or similar comment then categorize 'Racist comment on <whatever is the subject>'."
    #     f"If it is a sarcastic comment then categorize 'Sarcastic note on <whatever is the subject>'."
    #     F"Some examples: Sexist comment on the youtuber, Disappointment with Trump Administration, Appreciating the teachers' work, Happy to see the news"
    #     f"The category is: {category} and the comment is:\n\"{text}\""
    # )
    prompt = (
        f"Generate a concise sub-category for the given comment.\n"
        f"Use 5 to 6 words following the format: <Tone/Emotion> <Focus/Intent> <General Topic>.\n"
        f"Avoid specific names; use general topics instead.\n"
        f"The main category definitions are:\n" +
        "\n".join([f"- {label}: {definition}" for label, definition in label_definitions.items()]) +
        f"\n\nExamples:\n"
        f"- Sexist comment on the youtuber\n"
        f"- Disappointment with government policies\n"
        f"- Appreciating the teachers' work\n"
        f"- Happy to see the news\n"
        f"- Criticism towards educational reforms\n\n"
        f"Category: {category}\n"
        f"Comment: \"{text}\"\n"
        f"Return only the sub-category."
    )


    resp = model.generate_content(prompt)
    return resp.text.strip()

