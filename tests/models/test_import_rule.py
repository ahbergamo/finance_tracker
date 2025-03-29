import pytest
from app import db
from app.models.import_rule import ImportRule
from app.models.family import Family


def get_seeded_family():
    """
    Retrieve a seeded family.
    Assumes that a family with the name 'Family_1' exists.
    """
    family = Family.query.filter_by(name="Family_1").first()
    if not family:
        pytest.skip("Seeded family 'Family_1' not found.")
    return family


def get_seeded_import_rule():
    """
    Retrieve a seeded ImportRule.
    Assumes that an ImportRule with field_to_match 'Description'
    and match_pattern 'Payment Thank You - Web' exists.
    """
    rule = ImportRule.query.filter_by(
        field_to_match="Description",
        match_pattern="Payment Thank You - Web"
    ).first()
    if not rule:
        pytest.skip("Seeded ImportRule with field 'Description' and match_pattern 'Payment Thank You - Web' not found.")
    return rule


def test_import_rule_repr(app):
    """
    Verify that the __repr__ method returns the expected string.
    """
    rule = get_seeded_import_rule()
    expected = f"<ImportRule {rule.field_to_match} contains '{rule.match_pattern}' (Family ID: {rule.family_id})>"
    assert repr(rule) == expected


def test_override_category_display(app):
    """
    Verify that the override_category_display property returns the name
    of the override category if set.
    """
    rule = get_seeded_import_rule()
    # If the rule has an associated override category, its name should be returned.
    if rule.override_category_obj:
        expected = rule.override_category_obj.name
    else:
        expected = ""
    assert rule.override_category_display == expected


def test_override_category_display_without_category(app):
    """
    Verify that an ImportRule without an override category returns an empty string
    for override_category_display.
    """
    family = get_seeded_family()
    # Create an ImportRule without specifying an override_category_id.
    rule = ImportRule(
        account_type="Test Account",
        field_to_match="Test Field",
        match_pattern="Test Pattern",
        is_transfer=False,
        override_category_id=None,
        family_id=family.id
    )
    db.session.add(rule)
    db.session.commit()
    assert rule.override_category_display == ""
