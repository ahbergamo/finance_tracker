from flask import Blueprint


transactions_bp = Blueprint('transactions', __name__)

# Import submodules so their route definitions are registered with the blueprint
from app.routes.transactions import main                    # noqa: E402, F401
from app.routes.transactions import add_transaction         # noqa: E402, F401
from app.routes.transactions import edit_transaction        # noqa: E402, F401
from app.routes.transactions import delete_transaction      # noqa: E402, F401
from app.routes.transactions import import_transactions     # noqa: E402, F401
from app.routes.transactions import download_csv            # noqa: E402, F401
from app.routes.transactions import bulk_delete             # noqa: E402, F401
