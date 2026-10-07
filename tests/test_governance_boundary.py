from app.main import app


def test_runtime_api_has_only_authorized_editor_candidate_publication() -> None:
    # DATA_CONTRACT §13 / PRODUCT_SCOPE §14 authorize this isolated pilot.
    # Legacy Atlas/Airtable and canonical Globe publication remain unavailable.
    publish_routes = [route for route in app.routes if "publish" in getattr(route, "path", "").lower()]
    assert [route.path for route in publish_routes] == ["/api/knowledge-editor/drafts/{draft_id}/publish"]
    route = publish_routes[0]
    assert route.methods == {"POST"}
    from app.auth.service import get_current_user
    assert get_current_user in {dependency.call for dependency in route.dependant.dependencies}
    # Actual moderator, accepted digest and stale-pointer negatives are exercised
    # by tests/test_knowledge_editor.py, rather than inferred from a route name.
