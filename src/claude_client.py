import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = Anthropic(api_key=API_KEY)


def analyze_incident(incident):
    prompt = f"""
Analyze this ServiceNow incident and produce a triage recommendation.

Incident number: {incident.get("number")}
Short description: {incident.get("short_description")}
Description: {incident.get("description")}
Current category: {incident.get("category")}
Current priority: {incident.get("priority")}

Requirements:
- Recommend an appropriate category.
- Recommend a priority from 1 to 5.
- Recommend an assignment type.
- Give confidence between 0 and 1.
- Give a concise explanation.
- Do not invent facts not supported by the incident.
"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        output_config={
            "format": {
                "type": "json_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string"
                        },
                        "priority": {
                            "type": "integer",
                        },
                        "assignment_type": {
                            "type": "string"
                        },
                        "confidence": {
                            "type": "number",
                        },
                        "explanation": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "category",
                        "priority",
                        "assignment_type",
                        "confidence",
                        "explanation"
                    ],
                    "additionalProperties": False
                }
            }
        }
    )

    return json.loads(message.content[0].text)


def validate_recommendation(recommendation):
    if not 1 <= recommendation["priority"] <= 5:
        raise ValueError("Priority must be between 1 and 5")

    if not 0 <= recommendation["confidence"] <= 1:
        raise ValueError("Confidence must be between 0 and 1")

    if not recommendation["category"]:
        raise ValueError("Category cannot be empty")

    return recommendation



    