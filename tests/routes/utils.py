# tests/routes/utils.py
def login(client, username, password):
    """Helper to log in a user."""
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True
    )
