import json
from anthropic import Anthropic

from src.servicenow_client import (
    get_incident,
    search_incidents,
)

from src.knowledge import search_knowledge
from src.claude_client import API_KEY


client = Anthropic(api_key=API_KEY)


TOOLS = [
    {
        "name": "search_incidents",
        "description": (
            "Search ServiceNow incidents for related or similar issues."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string"
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_knowledge",
        "description": (
            "Search troubleshooting knowledge for relevant technical guidance."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string"
                }
            },
            "required": ["query"],
        },
    },
]


def execute_tool(name, tool_input):

    if name == "search_incidents":
        return search_incidents(tool_input["query"])

    if name == "search_knowledge":
        return search_knowledge(tool_input["query"])

    raise ValueError(f"Unknown tool: {name}")


def investigate_incident(number):
    incident = get_incident(number)

    if not incident:
        print(f"Incident {number} not found.")
        return None

    print(
        f"Investigating: {incident['number']} - "
        f"{incident['short_description']}"
    )

    messages = [
        {
            "role": "user",
            "content": (
                f"You are investigating this ServiceNow incident:\n\n"
                f"{json.dumps(incident)}\n\n"
                "Use the available tools to gather additional evidence. "
                "Search related incidents and technical knowledge when useful. "
                "Do not switch to another primary incident."
            ),
        }
    ]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            tools=TOOLS,
            messages=messages,
        )

        messages.append({
            "role": "assistant",
            "content": response.content,
        })

        tool_uses = [
            block
            for block in response.content
            if block.type == "tool_use"
        ]

        # Claude has finished using tools.
        # Generate the final structured recommendation.
        if not tool_uses:
            final_response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=500,
                messages=messages + [
                    {
                        "role": "user",
                        "content": (
                            "Using the investigation above, produce the final "
                            "incident triage recommendation."
                        ),
                    }
                ],
                output_config={
                    "format": {
                        "type": "json_schema",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "sys_id": {
                                    "type": "string"
                                },
                                "category": {
                                    "type": "string"
                                },
                                "priority": {
                                    "type": "integer"
                                },
                                "assignment_type": {
                                    "type": "string"
                                },
                                "confidence": {
                                    "type": "number"
                                },
                                "explanation": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "sys_id",
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

            return json.loads(
                final_response.content[0].text
            )

        # Execute any tools Claude requested.
        tool_results = []

        for tool_use in tool_uses:
            print(
                f"Claude called: {tool_use.name} "
                f"with {tool_use.input}"
            )

            result = execute_tool(
                tool_use.name,
                tool_use.input,
            )

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": json.dumps(result),
            })

        messages.append({
            "role": "user",
            "content": tool_results,
        })