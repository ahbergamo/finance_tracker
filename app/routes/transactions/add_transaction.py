from flask import request, redirect, url_for
from flask_login import login_required
from app.routes.transactions import transactions_bp
from app.services.transactions.add_transaction import process_add_transaction, render_add_transaction_form


@transactions_bp.route("/transactions/add", methods=["GET", "POST"])
@login_required
def add_transaction():
    if request.method == "POST":
        new_tx, error = process_add_transaction(request.form)
        if error == "redirect":
            return redirect(url_for("transactions.add_transaction"))
        return redirect(url_for("transactions.transactions"))
    return render_add_transaction_form()
