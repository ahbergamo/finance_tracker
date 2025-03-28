from flask import Blueprint, render_template


help_bp = Blueprint('help', __name__)


@help_bp.route("/help")
def help_page():
    """
    Route handler for the help page.

    Returns:
        Rendered HTML template for the help page.
    """
    # Render the help page template; Flask will handle errors automatically
    return render_template("help.html")
