import requests

import os
import requests
from dotenv import load_dotenv

load_dotenv()

INSTANCE_URL = os.getenv("SERVICENOW_INSTANCE_URL", "").rstrip("/")
CLIENT_ID = os.getenv("SERVICENOW_CLIENT_ID")
CLIENT_SECRET = os.getenv("SERVICENOW_CLIENT_SECRET")


def get_access_token():
    url = f"{INSTANCE_URL}/oauth_token.do"

    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    response = requests.post(
        url,
        data=data,
        headers={"Accept": "application/json"},
        timeout=30,
    )

    print("Token status:", response.status_code)

    response.raise_for_status()

    return response.json()["access_token"]


def get_incident(number):
    access_token = get_access_token()

    url = f"{INSTANCE_URL}/api/now/table/incident"

    params = {
        "sysparm_query": f"number={number}",
        "sysparm_limit": 1,
        "sysparm_fields": (
            "sys_id,number,short_description,description,"
            "priority,state,category,assignment_group"
        ),
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    results = response.json()["result"]

    if not results:
        return None

    return results[0]


def update_incident_ai_recommendation(sys_id, recommendation):
    access_token = get_access_token()

    url = f"{INSTANCE_URL}/api/now/table/incident/{sys_id}"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "u_ai_recommended_category": recommendation["category"],
        "u_ai_recommended_priority": recommendation["priority"],
        "u_ai_confidence": recommendation["confidence"],
        "u_ai_explanation": recommendation["explanation"],
    }

    response = requests.patch(
        url,
        headers=headers,
        json=payload,
        timeout=30,
    )

    print("Update status:", response.status_code)

    response.raise_for_status()

    return response.json()["result"]

def search_incidents(query, limit=5):
    access_token = get_access_token()

    url = f"{INSTANCE_URL}/api/now/table/incident"

    params = {
        "sysparm_query": (
            f"short_descriptionLIKE{query}"
            f"^ORdescriptionLIKE{query}"
        ),
        "sysparm_limit": limit,
        "sysparm_fields": (
            "sys_id,number,short_description,description,"
            "priority,state,category"
        ),
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()["result"]