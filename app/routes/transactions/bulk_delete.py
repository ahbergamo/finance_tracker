from flask import request
from flask_login import login_required
from app.routes.transactions import transactions_bp
from app.services.transactions.bulk_delete import build_transaction_query, handle_post_request, render_bulk_delete_page
from app.services.transactions.utilities import get_family_user_ids


@transactions_bp.route("/transactions/bulk_delete", methods=["GET", "POST"])
@login_required
def bulk_delete():
    family_user_ids = get_family_user_ids()
    query, filters = build_transaction_query(family_user_ids)
    if request.method == "POST":
        return handle_post_request(query, filters)
    return render_bulk_delete_page(query, filters)
