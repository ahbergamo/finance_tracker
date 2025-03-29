import io
import csv
from datetime import datetime
from dateutil import parser
from flask import render_template, redirect, url_for, flash, current_app, session
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.account_type import AccountType
from app.models.import_rule import ImportRule
from app import db
from app.services.transactions.utilities import get_family_user_ids, create_or_get_category
from sqlalchemy import func


# Batch size constant
PER_BATCH = 10


def get_account_type(account_id, current_user):
    try:
        acc_type_obj = AccountType.query.filter_by(id=account_id, family_id=current_user.family_id).first()
        if not acc_type_obj:
            flash(f"Invalid account selected (ID: {account_id}). Please try again.", "danger")
            current_app.logger.error("Invalid account selected: %s", account_id)
            return None
        current_app.logger.debug(
            "Account Type ID: %s, Name: %s, Date Field: %s, Description Field: %s, Amount Field: %s, Category Field: %s",
            acc_type_obj.id,
            acc_type_obj.name,
            acc_type_obj.date_field,
            acc_type_obj.description_field,
            acc_type_obj.amount_field,
            acc_type_obj.category_field,
        )
        return acc_type_obj
    except Exception as e:
        current_app.logger.error("Error retrieving account type for ID %s: %s", account_id, e)
        flash("An error occurred while retrieving the account type. Please try again.", "danger")
        return None


def validate_csv(file):
    if not file or not file.filename.lower().endswith(".csv"):
        flash("Invalid file format. Please upload a CSV file.", "danger")
        current_app.logger.warning("Invalid file format uploaded.")
        return False
    return True


def parse_csv(file, acc_type_obj, delimiter=","):
    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream, delimiter=delimiter)
        transactions_data = []

        for row in csv_input:
            transaction = parse_csv_row(row, acc_type_obj)
            if transaction:
                transactions_data.append(transaction)
        return transactions_data
    except Exception as e:
        current_app.logger.error("Error parsing CSV file: %s", e)
        flash("An error occurred while parsing the CSV file. Please check the file format and try again.", "danger")
        return []


def parse_csv_row(row, acc_type_obj):
    try:
        tx_date = parser.parse(row[acc_type_obj.date_field])
        description = row[acc_type_obj.description_field]
        if row.get("Memo"):
            description += " " + row["Memo"]
        amount = float(row[acc_type_obj.amount_field])
        if acc_type_obj.positive_expense:
            amount = -amount

        category_name = row.get(acc_type_obj.category_field, "").strip() or "Uncategorized"
        current_app.logger.debug(
            "Parsed Transaction - Date: %s, Description: %s, Amount: %s, Category: %s",
            tx_date,
            description,
            amount,
            category_name,
        )
        return (tx_date, description, amount, category_name)
    except KeyError as ke:
        current_app.logger.warning("Missing expected field in CSV row: %s. Row: %s", ke, row)
    except Exception as e:
        current_app.logger.error("Error processing CSV row: %s. Row: %s", e, row)
    return None


def apply_import_rules(transactions_data, acc_type_obj):
    processed_data = []
    rules = ImportRule.query.filter(
        (ImportRule.account_type.is_(None)) | (ImportRule.account_type == acc_type_obj.name)
    ).all()

    local_seen = set()  # Track keys within the current file

    for tx_date, description, amount, category_name in transactions_data:
        is_transfer, category_name = apply_rules_to_transaction(description, category_name, rules)
        category_obj = create_or_get_category(category_name)
        tx_key = (tx_date.date(), round(amount, 2))
        duplicate_in_file = tx_key in local_seen
        processed_data.append({
            "tx_date": tx_date.strftime("%m/%d/%Y"),
            "amount": amount,
            "description": description,
            "category_field": category_obj.name,
            "account_id": acc_type_obj.id,
            "account_name": acc_type_obj.name,
            "is_duplicate": duplicate_in_file,
            "tx_key": tx_key,
            "is_transfer": is_transfer
        })
        local_seen.add(tx_key)

    return processed_data


def apply_rules_to_transaction(description, category_name, rules):
    is_transfer = False
    for rule in rules:
        value = description if rule.field_to_match.lower() == "description" else category_name
        if rule.match_pattern in value:
            if rule.is_transfer:
                is_transfer = True
            if rule.override_category_id:
                category_name = rule.override_category_display
    return is_transfer, category_name


def check_duplicate(tx_date, amount, account_id, description):
    try:
        existing = Transaction.query.filter(
            Transaction.user_id.in_(get_family_user_ids()),
            func.date(Transaction.timestamp) == tx_date.date(),
            func.round(Transaction.amount, 2) == round(amount, 2),
            Transaction.account_id == account_id,
            Transaction.description == description
        ).first()
        return True if existing else False
    except Exception as e:
        current_app.logger.error(
            "Error checking duplicates for date %s, amount %s, account_id %s, description %s: %s",
            tx_date, amount, account_id, description, e
        )
        return False


def create_transaction_from_tx(tx, current_user):
    try:
        tx_date = datetime.strptime(tx["tx_date"], "%m/%d/%Y")
        amount = tx["amount"]
        description = tx["description"]
        account_id = tx["account_id"]
        category_name = tx["category_field"]
        is_transfer = tx.get("is_transfer", False)
        force_import = tx.get("force_import", False)

        category_obj = create_or_get_category(category_name)

        if check_duplicate(tx_date, amount, account_id, description) and not force_import:
            current_app.logger.debug(
                "Skipped duplicate transaction: Date=%s, Amount=%s, Description=%s",
                tx_date, amount, description
            )
            return False
        current_app.logger.debug(
            "Adding Transaction - Date: %s, Amount: %s, Description: %s, Account ID: %s, Category: %s, Is Transfer: %s",
            tx_date, amount, description, account_id, category_name, is_transfer,
        )
        new_tx = Transaction(
            amount=amount,
            description=description,
            timestamp=tx_date,
            user_id=current_user.id,
            category_id=category_obj.id,
            account_id=account_id,
            is_transfer=is_transfer,
        )
        db.session.add(new_tx)
        return True
    except Exception as e:
        current_app.logger.error("Error importing transaction: %s", e)
        return False


def update_tx_from_form(tx, i, form):
    key_cat = f"transactions[{i}][category_id]"
    if key_cat in form:
        selected_category_id = form.get(key_cat)
        if selected_category_id == "other":
            new_category = form.get(f"transactions[{i}][new_category]", "").strip()
            if new_category:
                tx["category_field"] = new_category
        elif selected_category_id:
            selected_category = Category.query.filter_by(id=selected_category_id, family_id=form.get('family_id')).first()
            if selected_category:
                tx["category_field"] = selected_category.name
        else:
            tx["category_field"] = form.get(f"transactions[{i}][category_field]", tx["category_field"])

    key_transfer = f"transactions[{i}][is_transfer]"
    if key_transfer in form:
        tx["is_transfer"] = form.get(key_transfer) == "on"

    key_force = f"transactions[{i}][force_import]"
    if key_force in form:
        tx["force_import"] = form.get(key_force) == "on"


def process_import_all(req, current_user):
    processed_data = session.get("processed_data")
    current_app.logger.info("Import All: session processed_data: %s", processed_data)
    if not processed_data:
        flash("No transactions to import.", "danger")
        return redirect(url_for("transactions.import_transactions"))

    for i, tx in enumerate(processed_data):
        update_tx_from_form(tx, i, req.form)
    session.modified = True

    newly_imported = 0
    for tx in processed_data:
        if create_transaction_from_tx(tx, current_user):
            newly_imported += 1

    session["total_imported"] = session.get("total_imported", 0) + newly_imported
    db.session.commit()
    session.pop("processed_data", None)
    session.pop("current_index", None)

    flash(f"Total imported: {session['total_imported']} transactions.", "success")
    session.pop("total_imported", None)
    return redirect(url_for("transactions.transactions"))


def process_file_upload(req, current_user):
    files = req.files.getlist("csv_file")
    if not files:
        flash("No files selected.", "danger")
        return redirect(url_for("transactions.import_transactions"))

    account_id = req.form.get("account_id", type=int)
    acc_type_obj = get_account_type(account_id, current_user)
    if not acc_type_obj:
        return redirect(url_for("transactions.import_transactions"))

    global_seen = set()
    all_processed_data = []
    for file in files:
        if not validate_csv(file):
            flash(f"File {file.filename} is not a valid CSV file.", "danger")
            continue
        file.stream.seek(0)
        transactions_data = parse_csv(file, acc_type_obj)
        processed_data = apply_import_rules(transactions_data, acc_type_obj)

        for tx in processed_data:
            tx_key = tx["tx_key"]
            tx_date_obj = datetime.strptime(tx["tx_date"], "%m/%d/%Y")
            duplicate_global = tx_key in global_seen
            duplicate_db = check_duplicate(tx_date_obj, tx["amount"], tx["account_id"], tx["description"])

            if duplicate_global or duplicate_db:
                tx["is_duplicate"] = True
                tx["force_import"] = False
            elif tx["is_duplicate"]:
                tx["force_import"] = True
            else:
                tx["force_import"] = False

        global_seen.update(tx["tx_key"] for tx in processed_data)
        all_processed_data.extend(processed_data)

    if not all_processed_data:
        flash("No valid transactions found in the uploaded files.", "danger")
        return redirect(url_for("transactions.import_transactions"))

    return prepare_import_preview(all_processed_data, current_user)


def process_batch_confirmation(req, current_user):
    processed_data = session.get("processed_data")
    current_app.logger.info("Batch confirmation: session processed_data: %s", processed_data)
    if not processed_data:
        flash("No transactions to import. Please start the import process again.", "danger")
        return redirect(url_for("transactions.import_transactions"))

    current_index = session.get("current_index", 0)
    batch_end = min(current_index + PER_BATCH, len(processed_data))
    for rel_idx, abs_idx in enumerate(range(current_index, batch_end)):
        update_tx_from_form(processed_data[abs_idx], rel_idx, req.form)
    session.modified = True

    imported_count = 0
    for i in range(current_index, batch_end):
        if create_transaction_from_tx(processed_data[i], current_user):
            imported_count += 1

    session["current_index"] += PER_BATCH
    session["total_imported"] += imported_count
    session.modified = True

    if session["current_index"] < len(processed_data):
        db.session.commit()
        batch_data = processed_data[session["current_index"]:session["current_index"] + PER_BATCH]
        categories = Category.query.filter_by(family_id=current_user.family_id).all()
        total_duplicates = sum(1 for tx in processed_data if tx["is_duplicate"])

        return render_template(
            "transactions/import_preview.html",
            transactions_data=batch_data,
            categories=categories,
            total_transactions=len(processed_data),
            total_imported=session["total_imported"],
            current_batch=(session["current_index"] // PER_BATCH) + 1,
            total_batches=(len(processed_data) + PER_BATCH - 1) // PER_BATCH,
            total_duplicates=total_duplicates
        )
    else:
        total_imported = session.pop("total_imported", 0)
        session.pop("processed_data", None)
        session.pop("current_index", None)
        db.session.commit()
        flash(f"Total imported: {total_imported} transactions.", "success")
        return redirect(url_for("transactions.transactions"))


def render_import_page_service(current_user):
    account_types = AccountType.query.filter_by(family_id=current_user.family_id).all()
    return render_template("transactions/import_transactions.html", accounts=account_types)


def prepare_import_preview(all_processed_data, current_user):
    try:
        session["processed_data"] = all_processed_data
        session["current_index"] = 0
        session["total_imported"] = 0
        session.modified = True

        batch_data = all_processed_data[:PER_BATCH]
        categories = Category.query.filter_by(family_id=current_user.family_id).all()
        total_duplicates = sum(1 for tx in all_processed_data if tx["is_duplicate"])
        return render_template(
            "transactions/import_preview.html",
            transactions_data=batch_data,
            categories=categories,
            total_transactions=len(all_processed_data),
            current_batch=1,
            total_batches=(len(all_processed_data) + PER_BATCH - 1) // PER_BATCH,
            total_imported=0,
            total_duplicates=total_duplicates
        )
    except Exception as e:
        current_app.logger.error("Error during session setup or rendering: %s", e)
        flash("An error occurred while preparing the import preview. Please try again.", "danger")
        return redirect(url_for("transactions.import_transactions"))
