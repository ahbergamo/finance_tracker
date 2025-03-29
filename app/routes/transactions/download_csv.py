from flask import request, current_app
from flask_login import login_required
from app.routes.transactions import transactions_bp
from app.services.transactions.download_csv import build_transaction_query, apply_time_filter, fetch_transactions, generate_csv_response
from app.services.transactions.utilities import get_family_user_ids


@transactions_bp.route("/transactions/download", methods=["GET"])
@login_required
def download_transactions_csv():
    try:
        filter_type = request.args.get("filter")
        time_filter = request.args.get("time_filter", "all")
        category_id = request.args.get("category_id", type=int)
        account_id = request.args.get("account_id", type=int)
        family_user_ids = get_family_user_ids()
        query = build_transaction_query(family_user_ids, filter_type, category_id, account_id)
        query = apply_time_filter(query, time_filter)
        transactions = fetch_transactions(query)
        return generate_csv_response(transactions)
    except Exception as e:
        current_app.logger.error("Error generating transactions CSV: %s", e)
        from flask import Response
        return Response("An error occurred while generating the CSV file.", status=500)
