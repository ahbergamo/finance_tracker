from datetime import date
from flask import render_template, request
from flask_login import login_required, current_user
from app.routes.reports import report_bp
from app.services.reports.retirement import (
    get_date_range,
    get_retirement_summary,
    get_retirement_chart_data,
    get_retirement_account_balances
)


@report_bp.route('/reports/retirement', methods=['GET'])
@login_required
def retirement_report():
    """
    Main route handler for the retirement report.
    Shows retirement account balances, contributions, and activity over time.
    """
    today = date.today()
    
    # Extract time filter and date range from request
    time_filter = request.args.get('time_filter', 'year')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Determine the date range
    start_date, end_date = get_date_range(today, time_filter, start_date_str, end_date_str)
    
    # Display string for date range
    date_range_display = f"{start_date.strftime('%B %d, %Y')} - {end_date.strftime('%B %d, %Y')}"
    
    # Get retirement summary data
    summary_data = get_retirement_summary(current_user, start_date, end_date)
    
    # Get chart data for contributions over time
    labels, totals = get_retirement_chart_data(current_user, start_date, end_date)
    
    # Get current account balances
    account_balances = get_retirement_account_balances(current_user, end_date)
    
    return render_template(
        'reports/retirement.html',
        summary_data=summary_data,
        account_balances=account_balances,
        labels=labels,
        totals=totals,
        date_range_display=date_range_display,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        time_filter=time_filter
    )