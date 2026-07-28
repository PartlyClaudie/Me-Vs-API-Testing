def validate_poll_creation(data):
    """Returns (valid: bool, error: str | None)."""
    if not data or not data.get("question"):
        return False, "question is required"

    options = data.get("options", [])
    if len(options) < 2:
        return False, "at least 2 options are required"

    return True, None