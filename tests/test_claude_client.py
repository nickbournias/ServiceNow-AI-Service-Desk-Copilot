import pytest

from src.claude_client import validate_recommendation


def _valid_recommendation(**overrides):
    recommendation = {
        "category": "network",
        "priority": 3,
        "confidence": 0.8,
        "explanation": "VPN gateway appears unreachable.",
    }
    recommendation.update(overrides)
    return recommendation


def test_validate_recommendation_accepts_valid_data():
    recommendation = _valid_recommendation()

    assert validate_recommendation(recommendation) == recommendation


@pytest.mark.parametrize(
    "overrides",
    [
        {"priority": 0},
        {"priority": 6},
        {"confidence": -0.1},
        {"confidence": 1.1},
        {"category": ""},
    ],
)
def test_validate_recommendation_rejects_invalid_values(overrides):
    recommendation = _valid_recommendation(**overrides)

    with pytest.raises(ValueError):
        validate_recommendation(recommendation)
