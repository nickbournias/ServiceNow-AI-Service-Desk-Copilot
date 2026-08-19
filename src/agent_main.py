from src.agent import investigate_incident
from src.claude_client import validate_recommendation
from src.servicenow_client import update_incident_ai_recommendation


def main():
    incident_number = input("Enter incident number: ").strip()

    if not incident_number:
        print("Incident number is required.")
        return

    recommendation = investigate_incident(incident_number)

    if not recommendation:
        print("No recommendation returned.")
        return

    recommendation = validate_recommendation(recommendation)

    print("\nClaude recommendation:")
    print("Category:", recommendation["category"])
    print("Priority:", recommendation["priority"])
    print("Assignment type:", recommendation["assignment_type"])
    print("Confidence:", recommendation["confidence"])
    print("Explanation:", recommendation["explanation"])

    # Human-in-the-loop approval
    approval = input(
        "\nApprove this recommendation? (y/n): "
    ).strip().lower()

    if approval != "y":
        print("\nRecommendation rejected. No ServiceNow changes made.")
        return

    update_incident_ai_recommendation(
        recommendation["sys_id"],
        recommendation,
    )

    print("\nRecommendation approved and written to ServiceNow.")


if __name__ == "__main__":
    main()