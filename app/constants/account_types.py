# List of default account types with their respective field mappings and configurations.
# Each account type is represented as a dictionary with the following keys:
# - name: The name of the account type.
# - category_field: The field used to categorize transactions.
# - date_field: The field representing the transaction date.
# - amount_field: The field representing the transaction amount.
# - description_field: The field containing the transaction description.
# - positive_expense: A boolean indicating whether positive amounts are considered expenses.

DEFAULT_ACCOUNT_TYPES = [
    # Chase Checking account configuration
    {
        "name": "Chase Checking",
        "category_field": "Type",
        "date_field": "Posting Date",
        "amount_field": "Amount",
        "description_field": "Description",
        "positive_expense": False,
    },
    # Discover Credit account configuration
    {
        "name": "Discover Credit",
        "category_field": "Category",
        "date_field": "Trans. Date",
        "amount_field": "Amount",
        "description_field": "Description",
        "positive_expense": True,
    },
    # US Bank Checking account configuration
    {
        "name": "US Bank Checking",
        "category_field": "Transaction",
        "date_field": "Date",
        "amount_field": "Amount",
        "description_field": "Name",
        "positive_expense": False,
    },
    # US Bank Savings account configuration
    {
        "name": "US Bank Savings",
        "category_field": "Transaction",
        "date_field": "Date",
        "amount_field": "Amount",
        "description_field": "Name",
        "positive_expense": False,
    }
]
