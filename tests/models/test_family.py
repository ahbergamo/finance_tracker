import pytest
from app import db
from app.models.family import Family


def get_seeded_family():
    """
    Returns a seeded family. Assumes a family with name 'Family_1' exists.
    """
    family = Family.query.filter_by(name="Family_1").first()
    if not family:
        pytest.skip("Seeded family 'Family_1' not found.")
    return family


def test_family_repr(app):
    """
    Verify that the __repr__ method returns the expected string.
    """
    family = get_seeded_family()
    expected = f"<Family {family.name}>"
    assert repr(family) == expected


def test_family_created_at(app):
    """
    Ensure that the seeded family has a non-null created_at timestamp.
    """
    family = get_seeded_family()
    assert family.created_at is not None


def test_family_unique_constraint(app):
    """
    Verify that creating a family with the same name as a seeded family violates
    the unique constraint.
    """
    family = get_seeded_family()
    duplicate = Family(name=family.name)
    db.session.add(duplicate)
    with pytest.raises(Exception):
        db.session.commit()
    db.session.rollback()
