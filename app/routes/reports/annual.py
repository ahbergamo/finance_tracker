from flask import render_template, request
from flask_login import login_required, current_user
from app.routes.reports import report_bp
from app.services.reports.annual import (
    parse_filters,
    get_family_user_ids,
    build_query,
    get_dropdown_options
)


@report_bp.route('/reports/annual', methods=['GET'])
@login_required
def annual_overview():
    """
    Render the annual overview report.
    """
    # 1. Parse filters
    filters = parse_filters(request.args)  # <--- Notice we pass in request.args

    # 2. Find all relevant user IDs
    family_user_ids = get_family_user_ids(current_user)

    # 3. Build the query
    query = build_query(filters, family_user_ids, current_user)
    if query is None:  # Means there was an invalid date format
        return render_template(
            'reports/annual_overview.html',
            annual_data=[],
            labels=[],
            incomes=[],
            expenses=[],
            start_date=filters['start_date'],
            end_date=filters['end_date'],
            selected_category=filters['category_id'],
            selected_account=filters['account_id'],
            categories=[],
            accounts=[]
        )

    # 4. Get dropdown options for the filter UI
    categories_list, accounts_list = get_dropdown_options(current_user)

    # 5. Execute the query and build arrays for the template/chart
    annual_data = []
    labels = []
    incomes = []
    expenses = []
    for row in query.all():
        year = int(row.year)
        total_income = row.total_income or 0
        total_expense = abs(row.total_expense) if row.total_expense else 0

        annual_data.append({
            'year': year,
            'total_income': total_income,
            'total_expense': total_expense,
            'net': total_income - total_expense
        })
        labels.append(str(year))
        incomes.append(total_income)
        expenses.append(total_expense)

    return render_template(
        'reports/annual_overview.html',
        annual_data=annual_data,
        labels=labels,
        incomes=incomes,
        expenses=expenses,
        start_date=filters['start_date'],
        end_date=filters['end_date'],
        selected_category=filters['category_id'],
        selected_account=filters['account_id'],
        categories=categories_list,
        accounts=accounts_list
    )
