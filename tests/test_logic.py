from logic import validate_poll_creation


def test_valid_poll_data_passes():
    valid, error = validate_poll_creation({
        "question": "Tabs or spaces?",
        "options": ["Tabs", "Spaces"]
    })
    assert valid is True
    assert error is None


def test_missing_question_is_rejected():
    valid, error = validate_poll_creation({
        "options": ["Tabs", "Spaces"]
    })
    assert valid is False
    assert error == "question is required"


def test_empty_question_string_is_rejected():
    valid, error = validate_poll_creation({
        "question": "",
        "options": ["Tabs", "Spaces"]
    })
    assert valid is False
    assert error == "question is required"


def test_missing_options_key_is_rejected():
    valid, error = validate_poll_creation({
        "question": "Tabs or spaces?"
    })
    assert valid is False
    assert error == "at least 2 options are required"


def test_only_one_option_is_rejected():
    valid, error = validate_poll_creation({
        "question": "Tabs or spaces?",
        "options": ["Tabs"]
    })
    assert valid is False
    assert error == "at least 2 options are required"


def test_none_data_is_rejected():
    valid, error = validate_poll_creation(None)
    assert valid is False
    assert error == "question is required"


def test_three_or_more_options_is_valid():
    valid, error = validate_poll_creation({
        "question": "Best language?",
        "options": ["Python", "JavaScript", "Go"]
    })
    assert valid is True

