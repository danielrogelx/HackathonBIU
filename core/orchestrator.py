def start_session(case: dict) -> dict:
    return {
        "phase": "opening",
        "personas": {
            "judge": "שופט ברירת מחדל — בכיר, מחמיר בנוהל",
            "attorney": "עו\"ד ברירת מחדל — תוקפן, מנוסה",
        },
        "opening_message": {
            "role": "judge",
            "content": "הדיון נפתח. עורך הדין, אנא הציג את טיעוניכם.",
        },
    }


def send_message(
    user_input: str,
    messages: list,
    phase: str,
    case: dict,
    personas: dict,
) -> dict:
    return {
        "judge_response": {
            "role": "judge",
            "content": f"[stub] שמעתי: {user_input}",
        },
        "attorney_response": {
            "role": "attorney",
            "content": "[stub] אני מתנגד לטענה זו!",
        },
        "new_phase": phase,
    }


def end_session(messages: list) -> dict:
    return {
        "scores": {
            "persuasion": 0,
            "law_knowledge": 0,
            "evidence": 0,
            "pressure_response": 0,
            "procedure": 0,
        },
        "strengths": [],
        "weaknesses": [],
        "errors": [],
        "recommendations": [],
    }
