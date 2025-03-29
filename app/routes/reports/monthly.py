from datetime import date
from flask import render_template, request
from flask_login import login_required, current_user
from app.routes.reports import report_bp
from app.services.reports.monthly import (
    get_date_range,
    get_family_filter,
    generate_chart_data,
    get_dropdown_options
)


@report_bp.route('/reports/monthly', methods=['GET'])
@login_required
def monthly_spending():
    """
    Main route handler for the monthly spending report.
    Retrieves and processes transaction data based on user filters.
    """
    today = date.today()

    # 1. Extract time_filter, category_id, account_id from request
    time_filter = request.args.get('time_filter', 'year')
    category_id = request.args.get('category_id', type=int)
    account_id = request.args.get('account_id', type=int)

    # If time_filter is custom, also retrieve start_date / end_date from request
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # 2. Determine the date range
    start_date, end_date = get_date_range(today, time_filter, start_date_str, end_date_str)

    # 3. Display string like "Month dd, yyyy - Month dd, yyyy"
    date_range_display = f"{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"

    # 4. Build the base query for transactions
    family_filter = get_family_filter(current_user)

    # 5. Generate chart data for negative amounts (spending)
    labels, totals = generate_chart_data(family_filter, start_date, end_date, category_id, account_id)

    # 6. Retrieve categories/accounts for dropdown filters
    categories, accounts = get_dropdown_options(current_user)

    # 7. Render the template
    return render_template(
        'reports/monthly.html',
        labels=labels,
        totals=totals,
        date_range_display=date_range_display,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        time_filter=time_filter,
        categories=categories,
        accounts=accounts,
        selected_category=category_id,
        selected_account=account_id
    )
