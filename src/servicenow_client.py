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


def get_incidents(limit=5):
    access_token = get_access_token()

    url = f"{INSTANCE_URL}/api/now/table/incident"

    params = {
        "sysparm_limit": limit,
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

    print("Incident status:", response.status_code)

    response.raise_for_status()

    return response.json()["result"]