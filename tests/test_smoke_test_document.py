from ict_cockpit.dev.smoke_test_document import SmokeTestDocument


SAMPLE = """# Smoke Test

### Startup

- [PASS] App opens.
- [QUESTION] State restores.
  - Restores data, but returns to the first review page.

### Runtime

- [NOT TESTED] Live path.
"""


def test_smoke_test_document_parses_validation_items_and_comments() -> None:
    document = SmokeTestDocument.from_text(SAMPLE)

    assert [item.text for item in document.items] == [
        "App opens.",
        "State restores.",
        "Live path.",
    ]
    assert [item.section for item in document.items] == [
        "Startup",
        "Startup",
        "Runtime",
    ]
    assert document.items[1].comments == [
        "Restores data, but returns to the first review page."
    ]
    assert document.summary() == {
        "PASS": 1,
        "FAIL": 0,
        "QUESTION": 1,
        "NOT TESTED": 1,
    }
    assert document.accepted is False


def test_smoke_test_document_round_trips_status_and_comment_changes() -> None:
    document = SmokeTestDocument.from_text(SAMPLE)

    document.update_item(
        1,
        status="PASS",
        comments=[
            "Originally questioned because the review page reset.",
            "Resolved as expected transient UI behavior.",
        ],
    )
    document.update_item(2, status="PASS", comments=[])

    rendered = document.to_text()

    assert "- [PASS] State restores." in rendered
    assert (
        "  - Originally questioned because the review page reset."
        in rendered
    )
    assert (
        "  - Resolved as expected transient UI behavior."
        in rendered
    )
    assert "- [PASS] Live path." in rendered
    assert document.accepted is True


def test_smoke_test_document_preserves_non_validation_markdown() -> None:
    document = SmokeTestDocument.from_text(SAMPLE)
    document.update_item(0, status="FAIL", comments=["Regression observed."])

    rendered = document.to_text()

    assert "# Smoke Test" in rendered
    assert "### Startup" in rendered
    assert "### Runtime" in rendered
    assert "- [FAIL] App opens." in rendered
    assert "  - Regression observed." in rendered


def test_smoke_test_document_rejects_unknown_status() -> None:
    document = SmokeTestDocument.from_text(SAMPLE)

    try:
        document.update_item(0, status="MAYBE")
    except ValueError as exc:
        assert "unsupported smoke-test status" in str(exc)
    else:
        raise AssertionError("expected unsupported status to raise")
