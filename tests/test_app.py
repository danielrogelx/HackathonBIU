from streamlit.testing.v1 import AppTest


def test_app_defaults_to_setup_screen():
    at = AppTest.from_file("app.py").run()
    assert not at.exception
    # Setup screen should show the submit button
    button_labels = [b.label for b in at.button]
    assert any("בחן" in label for label in button_labels)


def test_app_routes_to_chat_screen():
    at = AppTest.from_file("app.py")
    at.session_state["screen"] = "chat"
    at.session_state["phase"] = "opening"
    at.session_state["case"] = {
        "type": "criminal",
        "parties": "מדינה נ' ראובן",
        "charges": "גניבה",
        "evidence": "מצלמות",
        "judge_name": "",
        "attorney_name": "",
    }
    at.session_state["personas"] = {
        "judge": "שופט ברירת מחדל",
        "attorney": "עו\"ד ברירת מחדל",
    }
    at.session_state["messages"] = []
    at.run()
    assert not at.exception
    # Chat screen should show the send button
    button_labels = [b.label for b in at.button]
    assert any("שלח" in label for label in button_labels)
