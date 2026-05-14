from core.orchestrator import start_session, send_message, end_session


def test_start_session_returns_required_keys():
    case = {
        "type": "criminal",
        "parties": "מדינת ישראל נ' ראובן",
        "charges": "גניבה",
        "evidence": "תיעוד מצלמות",
        "judge_name": "",
        "attorney_name": "",
    }
    result = start_session(case)
    assert "phase" in result
    assert "personas" in result
    assert "opening_message" in result
    assert isinstance(result["phase"], str)
    assert isinstance(result["personas"], dict)
    assert "judge" in result["personas"]
    assert "attorney" in result["personas"]
    assert isinstance(result["opening_message"], dict)
    assert "role" in result["opening_message"]
    assert "content" in result["opening_message"]


def test_send_message_returns_required_keys():
    result = send_message(
        user_input="אני טוען כי הנאשם גנב את הרכב",
        messages=[],
        phase="opening",
        case={"type": "criminal"},
        personas={"judge": "שופט", "attorney": "עו\"ד"},
    )
    assert "judge_response" in result
    assert "attorney_response" in result
    assert "new_phase" in result
    assert isinstance(result["judge_response"], dict)
    assert "role" in result["judge_response"]
    assert "content" in result["judge_response"]
    assert isinstance(result["attorney_response"], dict)
    assert "role" in result["attorney_response"]
    assert "content" in result["attorney_response"]
    assert isinstance(result["new_phase"], str)


def test_end_session_returns_required_keys():
    messages = [{"role": "judge", "content": "הדיון נפתח"}]
    result = end_session(messages)
    assert "scores" in result
    assert "strengths" in result
    assert "weaknesses" in result
    assert "errors" in result
    assert "recommendations" in result
