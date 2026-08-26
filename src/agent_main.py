from src.agent import execute_write_action, investigate_incident
from src.claude_client import validate_recommendation
from src.logger import logger


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
        logger.info(
            "Recommendation rejected | incident=%s",
            incident_number,
        )

        print(
            "\nRecommendation rejected. "
            "No ServiceNow changes made."
        )
        return

    # Human approved the write action
    execute_write_action(
        recommendation,
        approved=True,
    )

    logger.info(
        "Recommendation approved | incident=%s",
        incident_number,
    )

    print(
        "\nRecommendation approved and written to ServiceNow."
    )


if __name__ == "__main__":
    main()
