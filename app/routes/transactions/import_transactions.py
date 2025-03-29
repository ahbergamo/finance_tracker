from flask import redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.routes.transactions import transactions_bp
from app.services.transactions.import_transaction import (
    process_import_all,
    process_file_upload,
    process_batch_confirmation,
    render_import_page_service
)


@transactions_bp.route("/transactions/import", methods=["GET", "POST"])
@login_required
def import_transactions():
    try:
        if request.method == "POST":
            if request.form.get("import_all") == "1":
                return process_import_all(request, current_user)
            elif request.form.get("confirm") != "1":
                return process_file_upload(request, current_user)
            elif request.form.get("confirm") == "1":
                return process_batch_confirmation(request, current_user)
        else:
            return render_import_page_service(current_user)
    except Exception as e:
        current_app.logger.error("Unexpected error in import_transactions route: %s", e)
        flash("An unexpected error occurred. Please try again.", "danger")
        return redirect(url_for("transactions.import_transactions"))
