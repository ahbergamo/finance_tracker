from flask import render_template, request, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.routes.reports import report_bp
from app.services.reports.income_expense import (
    get_date_filters,
    parse_date_range,
    get_family_user_ids,
    build_transaction_query,
    process_transaction_results,
    get_cached_categories,
    get_cached_accounts
)


@report_bp.route('/reports/income_expense', methods=['GET'])
@login_required
def income_expense():
    """
    Main route handler for the income and expense report.
    Retrieves filtered transaction data and renders the report template.
    """
    try:
        # 1. Retrieve/compute the start_date and end_date from request
        start_date, end_date = get_date_filters(request.args)

        # 2. Parse them into datetime objects
        start_dt, end_dt = parse_date_range(start_date, end_date)
        # For display: "MonthName day, year - MonthName day, year"
        date_range_display = f"{start_dt.strftime('%B %d, %Y')} - {end_dt.strftime('%B %d, %Y')}"

        # 3. Get other filters
        category_id = request.args.get('category_id', type=int)
        account_id = request.args.get('account_id', type=int)

        # 4. Get the list of user IDs to include (family or single user)
        family_user_ids = get_family_user_ids(current_user)

        # 5. Build the transaction query
        query = build_transaction_query(family_user_ids, start_dt, end_dt, category_id, account_id)

        # 6. Process results (aggregating income/expense by month)
        labels, incomes, expenses = process_transaction_results(query)

        # 7. Retrieve categories and accounts for dropdown filters
        categories_list = get_cached_categories(current_user)
        accounts_list = get_cached_accounts(current_user)

        # 8. Render the template
        return render_template(
            'reports/income_expense.html',
            labels=labels,
            incomes=incomes,
            expenses=expenses,
            start_date=start_date,
            end_date=end_date,
            date_range_display=date_range_display,
            categories=categories_list,
            accounts=accounts_list,
            selected_category=category_id,
            selected_account=account_id
        )

    except SQLAlchemyError:
        db.session.rollback()
        flash("An error occurred while processing your request. Please try again later.", "error")
        return render_template(
            'reports/income_expense.html',
            labels=[],
            incomes=[],
            expenses=[],
            start_date=None,
            end_date=None,
            date_range_display="",
            categories=[],
            accounts=[],
            selected_category=None,
            selected_account=None
        )
