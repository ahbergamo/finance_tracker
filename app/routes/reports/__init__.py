# app/routes/reports/__init__.py
from flask import Blueprint

report_bp = Blueprint('report', __name__)

# Import submodules so that their route definitions are registered with the blueprint.
from app.routes.reports import monthly          # noqa: E402, F401
from app.routes.reports import annual           # noqa: E402, F401
from app.routes.reports import income_expense   # noqa: E402, F401
