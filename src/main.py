from servicenow_client import get_incidents


def main():
    incidents = get_incidents()

    for incident in incidents:
        print(
            incident.get("number"),
            "-",
            incident.get("short_description"),
        )


if __name__ == "__main__":
    main()
