from streamlit.testing.v1 import AppTest


def _run_setup():
    at = AppTest.from_file("app.py").run()
    return at


def test_setup_form_renders_case_type_radio():
    at = _run_setup()
    assert not at.exception
    radio_options = at.radio[0].options
    assert "פלילי" in radio_options
    assert "אזרחי" in radio_options


def test_setup_form_has_required_fields():
    at = _run_setup()
    assert not at.exception
    # Should have at least 4 text inputs/areas: parties, charges, evidence, + 2 optional names
    assert len(at.text_input) + len(at.text_area) >= 3


def test_setup_form_submit_transitions_to_chat():
    at = _run_setup()
    # Fill required fields
    at.text_input[0].set_value("מדינת ישראל נ' ראובן")   # parties
    at.text_area[0].set_value("גניבה")                    # charges
    at.text_area[1].set_value("תיעוד מצלמות אבטחה")      # evidence
    # Click submit
    submit_buttons = [b for b in at.button if "בחן" in b.label]
    assert len(submit_buttons) == 1
    at = submit_buttons[0].click().run()
    assert not at.exception
    assert at.session_state["screen"] == "chat"
    assert at.session_state["phase"] == "opening"
    assert len(at.session_state["messages"]) == 1
    assert at.session_state["messages"][0]["role"] == "judge"
