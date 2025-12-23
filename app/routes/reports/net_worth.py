from flask import render_template
from flask_login import login_required, current_user
from app.routes.reports import report_bp
from app.services.reports.net_worth import (
    get_net_worth_summary,
    get_net_worth_history
)


@report_bp.route('/reports/net-worth', methods=['GET'])
@login_required
def net_worth_report():
    """
    Net worth report showing all accounts and total net worth.
    """
    # Get current net worth summary
    summary_data = get_net_worth_summary(current_user)

    # Get historical data for chart (12 months)
    history_data = get_net_worth_history(current_user, months=12)

    return render_template(
        'reports/net_worth.html',
        summary=summary_data['summary'],
        total_assets=summary_data['total_assets'],
        total_liabilities=summary_data['total_liabilities'],
        net_worth=summary_data['net_worth'],
        chart_labels=history_data['labels'],
        chart_net_worth=history_data['net_worth'],
        chart_assets=history_data['assets'],
        chart_liabilities=history_data['liabilities']
    )
