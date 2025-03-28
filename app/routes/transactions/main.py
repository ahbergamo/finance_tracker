from flask import render_template, request, current_app, flash, redirect, url_for, session
from flask_login import login_required
from app.routes.transactions import transactions_bp
from app.services.transactions.main import process_transactions_view


@transactions_bp.route("/transactions")
@login_required
def transactions():
    filter_type = request.args.get("filter", "normal")
    time_filter = request.args.get("time_filter", "all")
    category_id = request.args.get("category_id", type=int)
    category_ids_raw = request.args.get("category_ids")
    if category_ids_raw:
        category_ids = [int(cid) for cid in category_ids_raw.split(",") if cid.strip().isdigit()]
    else:
        category_ids = []
    account_id = request.args.get("account_id", type=int)
    page = request.args.get("page", 1, type=int)
    per_page = session.get("per_page", current_app.config.get("PER_PAGE", 10))

    view_data = process_transactions_view(filter_type, time_filter, category_id, category_ids, account_id, page, per_page)
    return render_template("transactions/index.html", **view_data)


@transactions_bp.route("/set_per_page", methods=["POST"])
@login_required
def set_per_page():
    try:
        per_page = int(request.form.get("per_page", 10))
        if per_page in [10, 25, 50]:
            session["per_page"] = per_page
            flash("Items per page updated.", "success")
        else:
            flash("Invalid selection.", "danger")
    except ValueError:
        flash("Invalid input.", "danger")
    return redirect(request.referrer or url_for("transactions.transactions"))
