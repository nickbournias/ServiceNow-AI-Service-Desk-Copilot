from pathlib import Path


KNOWLEDGE_DIR = Path("data/knowledge")


def search_knowledge(query, limit=3):
    query_words = query.lower().split()

    results = []

    for file_path in KNOWLEDGE_DIR.glob("*.md"):
        text = file_path.read_text()

        score = sum(
            1 for word in query_words
            if word in text.lower()
        )

        if score > 0:
            results.append({
                "title": file_path.stem,
                "content": text,
                "score": score,
            })

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:limit]
