from unittest.mock import MagicMock

from src.servicenow_client import get_incident, update_incident_ai_recommendation


def _mock_response(json_data, status_code=200):
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data
    response.raise_for_status = MagicMock()
    return response


def test_get_incident_returns_first_matching_result(monkeypatch):
    monkeypatch.setattr("src.servicenow_client.get_access_token", lambda: "fake-token")
    incident = {"sys_id": "abc123", "number": "INC0001", "short_description": "VPN down"}
    mock_get = MagicMock(return_value=_mock_response({"result": [incident]}))
    monkeypatch.setattr("src.servicenow_client.requests.get", mock_get)

    result = get_incident("INC0001")

    assert result == incident
    mock_get.assert_called_once()


def test_get_incident_returns_none_when_no_results(monkeypatch):
    monkeypatch.setattr("src.servicenow_client.get_access_token", lambda: "fake-token")
    mock_get = MagicMock(return_value=_mock_response({"result": []}))
    monkeypatch.setattr("src.servicenow_client.requests.get", mock_get)

    result = get_incident("INC9999")

    assert result is None


def test_update_incident_ai_recommendation_sends_expected_fields(monkeypatch):
    monkeypatch.setattr("src.servicenow_client.get_access_token", lambda: "fake-token")
    recommendation = {
        "sys_id": "abc123",
        "category": "network",
        "priority": 2,
        "confidence": 0.75,
        "explanation": "Likely VPN gateway outage.",
    }
    mock_patch = MagicMock(return_value=_mock_response({"result": {"sys_id": "abc123"}}))
    monkeypatch.setattr("src.servicenow_client.requests.patch", mock_patch)

    update_incident_ai_recommendation("abc123", recommendation)

    _, kwargs = mock_patch.call_args
    assert kwargs["json"] == {
        "u_ai_recommended_category": "network",
        "u_ai_recommended_priority": 2,
        "u_ai_confidence": 0.75,
        "u_ai_explanation": "Likely VPN gateway outage.",
    }
