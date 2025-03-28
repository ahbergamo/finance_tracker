import pytest
from app.models.import_rule import ImportRule
from tests.routes.utils import login
from app import db


@pytest.fixture(autouse=True)
def patch_process_override_category(monkeypatch):
    """
    Patch process_override_category in the import_rules module to handle two params:
    (form_data, family_id). Always returns 1 for simplicity in route tests.
    """
    from app.routes import import_rules

    def mock_process_override_category(form_data, family_id):
        return 1  # pretend override_category always yields ID=1

    monkeypatch.setattr(import_rules, "process_override_category", mock_process_override_category)


def test_import_rules_index(client):
    """
    Test that the import rules index page loads and displays expected content.
    """
    login(client, "user1", "test123")
    response = client.get("/import_rules")
    assert response.status_code == 200
    # Check for expected text (adjust based on your template)
    assert b"Import Rules" in response.data


def test_add_rule_get(client):
    """
    Test that the add rule page loads correctly.
    """
    login(client, "user1", "test123")
    response = client.get("/import_rules/add")
    assert response.status_code == 200
    # Expect the form to contain a label for "Field to Match"
    assert b"Field to Match" in response.data


def test_add_rule_post(client):
    """
    Test adding a new import rule via POST.
    """
    login(client, "user1", "test123")
    form_data = {
        "field_to_match": "Description",
        "match_pattern": "TEST_PATTERN",
        "is_transfer": "on",
        "override_category": "1"
    }
    response = client.post("/import_rules/add", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    # Check for a success flash message
    assert b"Import rule added successfully." in response.data
    # Verify in the database that the rule exists.
    with client.application.app_context():
        rule = ImportRule.query.filter_by(match_pattern="TEST_PATTERN").first()
        assert rule is not None


def test_edit_rule(client):
    """
    Test editing an existing import rule.
    """
    login(client, "user1", "test123")
    # First, add a rule that we will edit.
    form_data = {
        "field_to_match": "Description",
        "match_pattern": "EDIT_TEST",
        "is_transfer": "",
        "override_category": "1"
    }
    response = client.post("/import_rules/add", data=form_data, follow_redirects=True)
    assert b"Import rule added successfully." in response.data

    with client.application.app_context():
        rule = ImportRule.query.filter_by(match_pattern="EDIT_TEST").first()
        assert rule is not None
        rule_id = rule.id

    # Access the edit page.
    response = client.get(f"/import_rules/edit/{rule_id}")
    assert response.status_code == 200
    assert b"EDIT_TEST" in response.data

    # Post updated data.
    edit_data = {
        "field_to_match": "Description",
        "match_pattern": "EDITED_PATTERN",
        "is_transfer": "on",
        "override_category": "1"
    }
    response = client.post(f"/import_rules/edit/{rule_id}", data=edit_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Import rule updated successfully." in response.data
    with client.application.app_context():
        rule = db.session.get(ImportRule, rule_id)
        assert rule.match_pattern == "EDITED_PATTERN"


def test_delete_rule(client):
    """
    Test deleting an import rule.
    """
    login(client, "user1", "test123")
    # Add a rule to delete.
    form_data = {
        "field_to_match": "Description",
        "match_pattern": "DELETE_TEST",
        "is_transfer": "",
        "override_category": "1"
    }
    response = client.post("/import_rules/add", data=form_data, follow_redirects=True)
    assert b"Import rule added successfully." in response.data
    with client.application.app_context():
        rule = ImportRule.query.filter_by(match_pattern="DELETE_TEST").first()
        assert rule is not None
        rule_id = rule.id

    # Delete the rule.
    response = client.post(f"/import_rules/delete/{rule_id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"Import rule deleted successfully." in response.data
    with client.application.app_context():
        rule = db.session.get(ImportRule, rule_id)
        assert rule is None


def test_apply_rule(client):
    """
    Test applying an import rule.
    """
    login(client, "user1", "test123")
    # Add a rule to apply.
    form_data = {
        "field_to_match": "Description",
        "match_pattern": "APPLY_TEST",
        "is_transfer": "on",
        "override_category": "1"
    }
    response = client.post("/import_rules/add", data=form_data, follow_redirects=True)
    assert b"Import rule added successfully." in response.data
    with client.application.app_context():
        rule = ImportRule.query.filter_by(match_pattern="APPLY_TEST").first()
        assert rule is not None
        rule_id = rule.id

    # Simulate applying the rule.
    response = client.post(f"/import_rules/apply/{rule_id}", follow_redirects=True)
    assert response.status_code == 200
    # Since there may be no matching transactions, expect 0 updates.
    assert b"Rule applied to 0 transactions." in response.data


def test_rules_are_family_specific(client):
    """
    Test that import rules are only visible to members of the same family.

    A rule added by a member of one family (Family_1) should not appear
    when a member of another family (Awesome) views the rules.
    """
    login(client, "user1", "test123")
    form_data = {
        "field_to_match": "Description",
        "match_pattern": "FamilySpecificTest",
        "is_transfer": "",
        "override_category": "1"
    }
    response = client.post("/import_rules/add", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Import rule added successfully." in response.data

    # Log out and log in as a member of another family (Awesome, e.g., "frank" with password "asdded123").
    client.get("/logout", follow_redirects=True)
    login(client, "frank", "asdded123")
    response = client.get("/import_rules")
    # The rule "FamilySpecificTest" should NOT appear for a Awesome member.
    assert response.status_code == 200
    assert b"FamilySpecificTest" not in response.data
