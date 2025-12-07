from backend.app.utils.dedupe import dedupe_by_key


def test_dedupe_by_attr():
    items = [type("Item", (), {"url": "a"})(), type("Item", (), {"url": "a"})(), type("Item", (), {"url": "b"})()]
    result = dedupe_by_key(items, attr="url")
    assert len(result) == 2
