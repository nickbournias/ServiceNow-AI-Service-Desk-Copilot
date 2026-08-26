from src.knowledge import search_knowledge


def test_search_knowledge_returns_matches_sorted_by_relevance_and_respects_limit(
    tmp_path, monkeypatch
):
    monkeypatch.setattr("src.knowledge.KNOWLEDGE_DIR", tmp_path)
    (tmp_path / "vpn.md").write_text("vpn connection issue troubleshooting")
    (tmp_path / "wifi.md").write_text("wifi connection issue")
    (tmp_path / "network.md").write_text("network vpn issue")
    (tmp_path / "printer.md").write_text("printer paper jam")

    results = search_knowledge("vpn issue connection", limit=2)

    assert len(results) == 2
    assert results[0]["title"] == "vpn"
    assert results[0]["score"] == 3
    assert results[0]["score"] >= results[1]["score"]


def test_search_knowledge_returns_empty_list_when_no_match(tmp_path, monkeypatch):
    monkeypatch.setattr("src.knowledge.KNOWLEDGE_DIR", tmp_path)
    (tmp_path / "printer.md").write_text("printer paper jam")

    results = search_knowledge("vpn outage")

    assert results == []
