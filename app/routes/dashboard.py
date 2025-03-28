from sqlalchemy import func, extract, case
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.user import User
from flask import Blueprint, current_app, render_template, session, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
import datetime
import calendar
from dateutil.relativedelta import relativedelta
from app.models.budget import Budget


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/set_chart_slices", methods=["POST"])
@login_required
def set_chart_slices():
    """
    Update chart slice settings based on user input.
    """
    try:
        if "top_n_income" in request.form:
            session['income_chart_top_n'] = int(request.form.get("top_n_income", 10))
            flash("Income chart slice settings updated.", "success")
        elif "top_n_expense" in request.form:
            session['expense_chart_top_n'] = int(request.form.get("top_n_expense", 10))
            flash("Expense chart slice settings updated.", "success")
        elif "top_n_income_list" in request.form:
            session['income_list_top_n'] = int(request.form.get("top_n_income_list", 10))
            flash("Income list settings updated.", "success")
        elif "top_n_expense_list" in request.form:
            session['expense_list_top_n'] = int(request.form.get("top_n_expense_list", 10))
            flash("Expense list settings updated.", "success")
        else:
            flash("No settings provided.", "warning")
    except ValueError:
        flash("Invalid number provided.", "danger")
        current_app.logger.error("Invalid number provided.")
    return redirect(url_for("dashboard.dashboard"))


def get_family_user_ids():
    """
    Retrieve the list of user IDs for the current user or their family.
    """
    if current_user.family_id:
        try:
            family_users = User.query.filter_by(family_id=current_user.family_id).all()
            return [user.id for user in family_users]
        except Exception as e:
            current_app.logger.error(e)
            flash("Error retrieving family users.", "danger")
            return []
    return [current_user.id]


def calculate_totals(user_ids, year):
    """
    Calculate total income, expenses, and balance for the given user IDs and year.
    """
    try:
        total_income = (
            Transaction.query
            .filter(
                Transaction.user_id.in_(user_ids),
                Transaction.amount > 0,
                Transaction.is_transfer.is_(False),
                extract('year', Transaction.timestamp) == year
            )
            .with_entities(func.sum(Transaction.amount))
            .scalar() or 0
        )
        total_expenses = (
            Transaction.query
            .filter(
                Transaction.user_id.in_(user_ids),
                Transaction.amount < 0,
                Transaction.is_transfer.is_(False),
                extract('year', Transaction.timestamp) == year
            )
            .with_entities(func.sum(Transaction.amount))
            .scalar() or 0
        )
        return total_income, abs(total_expenses), total_income - abs(total_expenses)
    except Exception as e:
        current_app.logger.error(e)
        flash("Error calculating totals.", "danger")
        return 0, 0, 0


def get_monthly_data(user_ids, start_date, end_date):
    """
    Retrieve monthly income and expense data for the given user IDs and date range.
    """
    try:
        monthly_data = (
            db.session.query(
                extract('year', Transaction.timestamp).label("year"),
                extract('month', Transaction.timestamp).label("month"),
                func.sum(case((Transaction.amount < 0, Transaction.amount), else_=0)).label("expenses"),
                func.sum(case((Transaction.amount > 0, Transaction.amount), else_=0)).label("income")
            )
            .filter(
                Transaction.user_id.in_(user_ids),
                Transaction.is_transfer.is_(False),
                Transaction.timestamp >= start_date,
                Transaction.timestamp <= end_date
            )
            .group_by("year", "month")
            .all()
        )
        return monthly_data
    except Exception as e:
        current_app.logger.error(e)
        flash("Error retrieving monthly data.", "danger")
        return []


def get_category_totals(user_ids, start_date, end_date):
    """
    Retrieve category totals for income and expenses.
    """
    try:
        category_totals = (
            db.session.query(Category, func.sum(Transaction.amount).label("total"))
            .join(Transaction, Transaction.category_id == Category.id)
            .filter(
                Transaction.user_id.in_(user_ids),
                Transaction.is_transfer.is_(False),
                Transaction.timestamp >= start_date,
                Transaction.timestamp <= end_date,
                Category.family_id == current_user.family_id
            )
            .group_by(Category.id)
            .all()
        )
        return category_totals
    except Exception as e:
        current_app.logger.error(e)
        flash("Error retrieving category totals.", "danger")
        return []


def get_budget_details(user_ids):
    """
    Retrieve budget details for the given user IDs.
    """
    try:
        budgets = Budget.query.filter(Budget.user_id.in_(user_ids)).all()
        budget_details = []
        for b in budgets:
            budgeted = b.amount
            category_ids = [c.id for c in b.categories]
            spent = db.session.query(func.sum(Transaction.amount)).filter(
                Transaction.user_id.in_(user_ids),
                Transaction.category_id.in_(category_ids),
                Transaction.timestamp >= b.start_date,
                Transaction.timestamp <= b.end_date
            ).scalar() or 0
            budget_details.append({
                'name': b.name,
                'budgeted': budgeted,
                'spent': abs(spent),
                'remaining': budgeted - abs(spent)
            })
        return budget_details
    except Exception as e:
        current_app.logger.error(e)
        flash("Error retrieving budget details.", "danger")
        return []


def compute_monthly_totals(user_ids, start_date, end_date):
    """
    Compute monthly income and expense totals for the given user IDs and date range.
    """
    monthly_data = get_monthly_data(user_ids, start_date, end_date)
    monthly_expenses = []
    monthly_income = []
    month_labels = []
    monthly_lookup = {(int(row.year), int(row.month)): row for row in monthly_data}
    current_date = start_date
    while current_date <= end_date:
        yr, mo = current_date.year, current_date.month
        row = monthly_lookup.get((yr, mo))
        income = row.income if row and row.income is not None else 0
        expenses = abs(row.expenses) if row and row.expenses is not None else 0
        monthly_income.append(income)
        monthly_expenses.append(expenses)
        month_labels.append(current_date.strftime("%b"))
        current_date = (current_date.replace(day=1) + relativedelta(months=1))
    return monthly_income, monthly_expenses, month_labels


def process_category_totals(category_totals, top_n):
    """
    Process category totals to compute top N items and the "Rest" aggregation.
    """
    sorted_totals = sorted(
        [(cat, abs(total)) for cat, total in category_totals],
        key=lambda x: x[1], reverse=True
    )
    top, rest = top_with_rest(sorted_totals, top_n)
    labels = [cat.name for cat, total in top]
    data = [total for cat, total in top]
    ids = [cat.id for cat, total in top]
    if rest is not None:
        rest_ids = [cat.id for cat, total in sorted_totals[len(top):]]
        labels.append("Rest")
        data.append(rest)
        ids.append(0)
    else:
        rest_ids = []
    return labels, data, ids, rest_ids


def prepare_cash_flow_data(user_ids, year, month):
    """
    Prepare cash flow data for the current month.
    """
    transactions = Transaction.query.filter(
        Transaction.user_id.in_(user_ids),
        Transaction.is_transfer.is_(False),
        extract('year', Transaction.timestamp) == year,
        extract('month', Transaction.timestamp) == month
    ).order_by(Transaction.timestamp.asc()).all()
    cash_flow_dates = []
    cash_flow_data = []
    cumulative = 0
    for tx in transactions:
        cumulative += tx.amount
        cash_flow_dates.append(tx.timestamp.strftime("%Y-%m-%d"))
        cash_flow_data.append(cumulative)
    return cash_flow_dates, cash_flow_data


def top_with_rest(cat_totals, top_n):
    """
    Extract the top N items from a list of category totals and compute the "Rest" aggregation.

    Args:
        cat_totals (list): A list of tuples (category, total).
        top_n (int): The number of top items to extract.

    Returns:
        tuple: A tuple containing the top N items and the sum of the remaining items.
    """
    if len(cat_totals) <= top_n:
        return cat_totals, None
    top = cat_totals[:top_n]
    rest_total = sum(total for cat, total in cat_totals[top_n:])
    return top, rest_total


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    """
    Render the dashboard with user-specific financial data.
    """
    # Retrieve user-configured settings
    income_chart_top_n = session.get('income_chart_top_n', 10)
    expense_chart_top_n = session.get('expense_chart_top_n', 10)
    income_list_top_n = session.get('income_list_top_n', 10)
    expense_list_top_n = session.get('expense_list_top_n', 10)

    # Get user IDs for the current user or their family
    family_user_ids = get_family_user_ids()

    # Calculate overall totals for the current year
    current_year = datetime.datetime.now().year
    total_income, total_expenses, balance = calculate_totals(family_user_ids, current_year)

    # Compute monthly totals for the past 12 months
    today = datetime.date.today()
    current_month_start = today.replace(day=1)
    start_date = current_month_start - relativedelta(months=11)
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_date = today.replace(day=last_day)
    monthly_income, monthly_expenses, month_labels = compute_monthly_totals(family_user_ids, start_date, end_date)

    # Retrieve and process category totals
    category_totals = get_category_totals(family_user_ids, start_date, end_date)
    income_category_totals_all = [(cat, total) for cat, total in category_totals if total > 0]
    expense_category_totals_all = [(cat, total) for cat, total in category_totals if total < 0]

    income_labels, income_data, income_ids, income_rest_ids = process_category_totals(income_category_totals_all, income_chart_top_n)
    expense_labels, expense_data, expense_ids, expense_rest_ids = process_category_totals(expense_category_totals_all, expense_chart_top_n)

    # For lists: slice the complete sorted lists
    income_category_list = income_category_totals_all[:income_list_top_n]
    expense_category_list = expense_category_totals_all[:expense_list_top_n]

    # Retrieve recent transactions
    recent_transactions = Transaction.query.filter(
        Transaction.user_id.in_(family_user_ids)
    ).order_by(Transaction.timestamp.desc()).limit(5).all()

    # Retrieve budget details
    budget_details = get_budget_details(family_user_ids)

    # Prepare cash flow data for the current month
    cash_flow_dates, cash_flow_data = prepare_cash_flow_data(family_user_ids, today.year, today.month)

    # Prepare pie chart date range
    pie_start_date = start_date.strftime("%Y-%m-%d")
    pie_end_date = end_date.strftime("%Y-%m-%d")

    return render_template("dashboard.html",
                           total_income=total_income,
                           total_expenses=total_expenses,
                           balance=balance,
                           income_category_totals=income_category_totals_all,  # for chart filtering if needed
                           expense_category_totals=expense_category_totals_all,
                           current_year=current_year,
                           monthly_expenses=monthly_expenses,
                           monthly_income=monthly_income,
                           monthLabels=month_labels,
                           expense_categories_labels=expense_labels,
                           expense_categories_data=expense_data,
                           income_categories_labels=income_labels,
                           income_categories_data=income_data,
                           recent_transactions=recent_transactions,
                           budget_details=budget_details,
                           cash_flow_dates=cash_flow_dates,
                           cash_flow_data=cash_flow_data,
                           pieStartDate=pie_start_date,
                           pieEndDate=pie_end_date,
                           expenseCategoriesIds=expense_ids,
                           expenseCategoriesRestIds=expense_rest_ids,
                           incomeCategoriesIds=income_ids,
                           incomeCategoriesRestIds=income_rest_ids,
                           income_chart_top_n=income_chart_top_n,
                           expense_chart_top_n=expense_chart_top_n,
                           income_list_top_n=income_list_top_n,
                           expense_list_top_n=expense_list_top_n,
                           income_category_list=income_category_list,
                           expense_category_list=expense_category_list
                           )
