from streamlit.testing.v1 import AppTest


def _run_chat(messages=None):
    at = AppTest.from_file("app.py")
    at.session_state["screen"] = "chat"
    at.session_state["phase"] = "opening"
    at.session_state["case"] = {
        "type": "criminal",
        "parties": "מדינה נ' ראובן",
        "charges": "גניבה",
        "evidence": "מצלמות",
        "judge_name": "שופט כהן",
        "attorney_name": "",
    }
    at.session_state["personas"] = {
        "judge": "שופט ברירת מחדל",
        "attorney": "עו\"ד ברירת מחדל",
    }
    at.session_state["messages"] = messages or []
    return at.run()


def test_chat_view_renders_phase_header():
    at = _run_chat()
    assert not at.exception
    subheader_texts = [s.value for s in at.subheader]
    assert any("פתיחה" in t for t in subheader_texts)


def test_chat_view_renders_judge_message():
    messages = [{"role": "judge", "content": "הדיון נפתח"}]
    at = _run_chat(messages)
    assert not at.exception
    all_markdown = " ".join(m.value for m in at.markdown)
    assert "הדיון נפתח" in all_markdown
    assert "🔵" in all_markdown


def test_chat_view_renders_attorney_message():
    messages = [{"role": "attorney", "content": "אני מתנגד"}]
    at = _run_chat(messages)
    assert not at.exception
    all_markdown = " ".join(m.value for m in at.markdown)
    assert "אני מתנגד" in all_markdown
    assert "🔴" in all_markdown


def test_chat_view_has_send_and_end_buttons():
    at = _run_chat()
    assert not at.exception
    button_labels = [b.label for b in at.button]
    assert any("שלח" in label for label in button_labels)
    assert any("סיים" in label for label in button_labels)
