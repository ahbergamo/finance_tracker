
from flask import current_app
from app.models.pre_defined_account import PreDefinedAccount
from app.constants.account_types import DEFAULT_ACCOUNT_TYPES
from app import db


def ensure_default_account_types():
    for entry in DEFAULT_ACCOUNT_TYPES:
        if not PreDefinedAccount.query.filter_by(name=entry["name"]).first():
            db.session.add(PreDefinedAccount(**entry))
    db.session.commit()


if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        print("App context active, current_app:", current_app.name)
        ensure_default_account_types()
