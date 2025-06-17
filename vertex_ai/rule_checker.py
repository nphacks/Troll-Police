from google import genai
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

# Uses Gemini AI to check if a comment violates specified content rules.
# Sends a prompt with rules and comment text, expects structured JSON response indicating violations and reasons.
# Returns list of violated rules if any, otherwise empty list.

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

class RuleViolationResult(BaseModel):
    violated: bool
    reasons: list[str]

def violates_content_rules(text, content_rules):    
    prompt = (
        f"Check if the following YouTube comment violates any of the given content rules.\n"
        f"Return:\n"
        f"- violated: true or false\n"
        f"- reasons: List of specific rules violated (quote exact rule)\n\n"
        f"Content Rules:\n" + "\n".join([f"- {rule}" for rule in content_rules]) +
        f"\n\nComment:\n\"{text}\""
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": RuleViolationResult,
        },
    )

    # print('Yes comming to rule checker')

    return response.parsed.reasons if response.parsed.violated else []