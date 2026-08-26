import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.agent import execute_tool, execute_write_action, investigate_incident


def test_execute_tool_dispatches_known_tools_and_rejects_unknown(monkeypatch):
    monkeypatch.setattr("src.agent.search_incidents", lambda query: [{"query": query}])
    monkeypatch.setattr("src.agent.search_knowledge", lambda query: [{"kb": query}])

    assert execute_tool("search_incidents", {"query": "vpn"}) == [{"query": "vpn"}]
    assert execute_tool("search_knowledge", {"query": "vpn"}) == [{"kb": "vpn"}]

    with pytest.raises(ValueError):
        execute_tool("delete_incident", {})


def test_execute_write_action_blocks_unapproved_writes(monkeypatch):
    mock_update = MagicMock()
    monkeypatch.setattr("src.servicenow_client.update_incident_ai_recommendation", mock_update)

    with pytest.raises(PermissionError):
        execute_write_action({"sys_id": "abc123"}, approved=False)

    mock_update.assert_not_called()


def test_execute_write_action_writes_when_approved(monkeypatch):
    mock_update = MagicMock(return_value={"sys_id": "abc123"})
    monkeypatch.setattr("src.servicenow_client.update_incident_ai_recommendation", mock_update)
    recommendation = {"sys_id": "abc123", "category": "network"}

    result = execute_write_action(recommendation, approved=True)

    mock_update.assert_called_once_with("abc123", recommendation)
    assert result == {"sys_id": "abc123"}


def test_investigate_incident_returns_none_when_incident_not_found(monkeypatch):
    monkeypatch.setattr("src.agent.get_incident", lambda number: None)

    assert investigate_incident("INC0000") is None


def test_investigate_incident_runs_tool_loop_and_returns_recommendation(monkeypatch):
    incident = {"number": "INC0001", "short_description": "VPN down", "sys_id": "abc123"}
    monkeypatch.setattr("src.agent.get_incident", lambda number: incident)
    monkeypatch.setattr("src.agent.execute_tool", lambda name, tool_input: {"found": "evidence"})

    tool_use_block = SimpleNamespace(
        type="tool_use", name="search_knowledge", input={"query": "vpn"}, id="toolu_1"
    )
    investigation_response = SimpleNamespace(content=[tool_use_block])
    no_tool_response = SimpleNamespace(
        content=[SimpleNamespace(type="text", text="Investigation complete.")]
    )

    recommendation = {
        "sys_id": "abc123",
        "category": "network",
        "priority": 2,
        "assignment_type": "network_team",
        "confidence": 0.9,
        "explanation": "VPN gateway outage confirmed.",
    }
    final_response = SimpleNamespace(
        content=[SimpleNamespace(type="text", text=json.dumps(recommendation))]
    )

    mock_client = MagicMock()
    mock_client.messages.create.side_effect = [
        investigation_response,
        no_tool_response,
        final_response,
    ]
    monkeypatch.setattr("src.agent.client", mock_client)

    result = investigate_incident("INC0001")

    assert result == recommendation
    assert mock_client.messages.create.call_count == 3


def test_investigate_incident_raises_runtime_error_after_max_rounds(monkeypatch):
    incident = {"number": "INC0001", "short_description": "VPN down", "sys_id": "abc123"}
    monkeypatch.setattr("src.agent.get_incident", lambda number: incident)
    monkeypatch.setattr("src.agent.execute_tool", lambda name, tool_input: {"found": "evidence"})

    tool_use_block = SimpleNamespace(
        type="tool_use", name="search_knowledge", input={"query": "vpn"}, id="toolu_1"
    )
    always_tool_response = SimpleNamespace(content=[tool_use_block])

    mock_client = MagicMock()
    mock_client.messages.create.return_value = always_tool_response
    monkeypatch.setattr("src.agent.client", mock_client)

    with pytest.raises(RuntimeError):
        investigate_incident("INC0001")
