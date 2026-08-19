from servicenow_client import (
    get_incidents,
    update_incident_ai_recommendation,
)

from claude_client import (
    analyze_incident,
    validate_recommendation,
)

def main():
    incidents = get_incidents(limit=1)

    if not incidents:
        print("No incidents found")
        return

    incident = incidents[0]

    print("\nIncident:")
    print(
        incident.get("number"),
        "-",
        incident.get("short_description"),
    )

    recommendation = analyze_incident(incident)
    recommendation = validate_recommendation(recommendation)

    print("\nClaude recommendation:")
    print("Category:", recommendation["category"])
    print("Priority:", recommendation["priority"])
    print("Assignment type:", recommendation["assignment_type"])
    print("Confidence:", recommendation["confidence"])
    print("Explanation:", recommendation["explanation"])

    updated_incident = update_incident_ai_recommendation(
        incident["sys_id"], recommendation,
    )
    
    print("\nRecommendation written to ServiceNow.")


if __name__ == "__main__":
    main()