# Data Engineering Student 1 — Streamlit Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Streamlit frontend for the Hebrew court simulation app (מתמחה בבית המשפט) — setup form, chat interface, and RTL routing — with stub orchestrator functions that Person 1 will replace with real logic.

**Architecture:** Thin router in `app.py` dispatches to screen-specific `render()` functions in `ui/`. All state lives in `st.session_state`. `core/orchestrator.py` defines the four interface contract functions as stubs so the UI can be built and tested independently.

**Tech Stack:** Python 3.11+, Streamlit ≥1.40, pytest, streamlit.testing.v1

---

## File Map

| File | Status | Responsibility |
|---|---|---|
| `requirements.txt` | Create | Python dependencies |
| `.env.example` | Create | Environment variable template |
| `core/__init__.py` | Create | Package marker |
| `core/orchestrator.py` | Create | Interface contract stubs (Person 1 fills bodies) |
| `ui/__init__.py` | Create | Package marker |
| `ui/setup_form.py` | Create | Case setup screen |
| `ui/chat_view.py` | Create | Simulation chat screen |
| `app.py` | Create | RTL CSS + screen router |
| `tests/__init__.py` | Create | Package marker |
| `tests/test_orchestrator.py` | Create | Stub contract shape tests |
| `tests/test_app.py` | Create | Router smoke tests |
| `tests/test_setup_form.py` | Create | Setup form interaction tests |
| `tests/test_chat_view.py` | Create | Chat view render + interaction tests |

---

## Task 1: Project Scaffold

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `core/__init__.py`
- Create: `ui/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create `requirements.txt`**

```
streamlit>=1.40.0
httpx>=0.27.0
python-dotenv>=1.0.0
firecrawl-py>=1.0.0
pydantic>=2.0.0
pytest>=8.0.0
```

- [ ] **Step 2: Create `.env.example`**

```
OPENROUTER_API_KEY=your_key_here
```

- [ ] **Step 3: Create package markers**

Create `core/__init__.py`, `ui/__init__.py`, and `tests/__init__.py` — all empty files.

- [ ] **Step 4: Install dependencies**

Run: `pip install -r requirements.txt`

Expected: All packages install without errors.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt .env.example core/__init__.py ui/__init__.py tests/__init__.py
git commit -m "feat: project scaffold and dependencies"
```

---

## Task 2: Interface Contract (`core/orchestrator.py`)

**Files:**
- Create: `tests/test_orchestrator.py`
- Create: `core/orchestrator.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_orchestrator.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_orchestrator.py -v`

Expected: `ModuleNotFoundError: No module named 'core.orchestrator'`

- [ ] **Step 3: Write the stubs**

Create `core/orchestrator.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_orchestrator.py -v`

Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add core/orchestrator.py tests/test_orchestrator.py
git commit -m "feat: orchestrator interface contract stubs"
```

---

## Task 3: `app.py` — RTL CSS + Router

**Files:**
- Create: `tests/test_app.py`
- Create: `app.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_app.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_app.py -v`

Expected: `FileNotFoundError` or `ModuleNotFoundError` since `app.py` doesn't exist yet.

- [ ] **Step 3: Write `app.py`**

```python
import streamlit as st

st.markdown(
    "<style>body, .stApp, .stMarkdown { direction: rtl; text-align: right; }</style>",
    unsafe_allow_html=True,
)

screen = st.session_state.get("screen", "setup")

if screen == "setup":
    from ui.setup_form import render
    render()
elif screen == "chat":
    from ui.chat_view import render
    render()
elif screen == "debrief":
    st.info("טוען דוח מאמן... (בקרוב)")
```

- [ ] **Step 4: Create placeholder `ui/setup_form.py` and `ui/chat_view.py` so imports resolve**

Create `ui/setup_form.py` with just:
```python
import streamlit as st

def render():
    if st.button("בחן אותי!"):
        pass
```

Create `ui/chat_view.py` with just:
```python
import streamlit as st

def render():
    if st.button("שלח"):
        pass
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_app.py -v`

Expected: 2 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add app.py ui/setup_form.py ui/chat_view.py tests/test_app.py
git commit -m "feat: app router with RTL CSS and screen routing"
```

---

## Task 4: `ui/setup_form.py`

**Files:**
- Create: `tests/test_setup_form.py`
- Modify: `ui/setup_form.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_setup_form.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_setup_form.py -v`

Expected: `AssertionError` on radio options (placeholder form doesn't have them yet).

- [ ] **Step 3: Write full `ui/setup_form.py`**

```python
import streamlit as st
from core.orchestrator import start_session


def render():
    st.title("מתמחה בבית המשפט 🏛️")
    st.subheader("סימולטור דיון משפטי לעורכי דין")

    case_type = st.radio("סוג תיק", ["פלילי", "אזרחי"], horizontal=True)

    parties = st.text_input("הצדדים *", placeholder="לדוגמה: מדינת ישראל נ' ראובן שמעון")
    charges = st.text_area("האישום / התביעה *", placeholder="תאר את האישום הפלילי או עילת התביעה")
    evidence = st.text_area("ראיות מרכזיות *", placeholder="פרט את הראיות המרכזיות שברשותך")

    st.markdown("---")
    st.markdown("**אופציונלי — ניתן להשאיר ריק לקבל פרסונות ברירת מחדל**")
    judge_name = st.text_input("שם השופט", placeholder="לדוגמה: אסתר חיות")
    attorney_name = st.text_input("שם עו\"ד הצד שכנגד", placeholder="לדוגמה: דן מרידור")

    if st.button("בחן אותי! ⚖️", type="primary"):
        if not parties or not charges or not evidence:
            st.error("יש למלא את כל השדות המסומנים ב-*")
            return

        case = {
            "type": "criminal" if case_type == "פלילי" else "civil",
            "parties": parties,
            "charges": charges,
            "evidence": evidence,
            "judge_name": judge_name,
            "attorney_name": attorney_name,
        }

        with st.spinner("מכין את הסימולציה..."):
            result = start_session(case)

        st.session_state["case"] = case
        st.session_state["personas"] = result["personas"]
        st.session_state["phase"] = result["phase"]
        st.session_state["messages"] = [result["opening_message"]]
        st.session_state["screen"] = "chat"
        st.rerun()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_setup_form.py -v`

Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add ui/setup_form.py tests/test_setup_form.py
git commit -m "feat: setup form with case type, fields, and session transition"
```

---

## Task 5: `ui/chat_view.py` — Message Display

**Files:**
- Create: `tests/test_chat_view.py`
- Modify: `ui/chat_view.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_chat_view.py`:

```python
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
    # Phase header should appear as a subheader
    subheader_texts = [s.value for s in at.subheader]
    assert any("פתיחה" in t for t in subheader_texts)


def test_chat_view_renders_judge_message():
    messages = [{"role": "judge", "content": "הדיון נפתח"}]
    at = _run_chat(messages)
    assert not at.exception
    # Judge message text should appear somewhere in rendered markdown
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_chat_view.py -v`

Expected: Failures on phase header content and message rendering (placeholder chat_view doesn't have these).

- [ ] **Step 3: Write full `ui/chat_view.py`**

```python
import streamlit as st
from core.orchestrator import send_message, end_session

PHASE_LABELS = {
    "opening": "פתיחה",
    "evidence": "הצגת הוכחות",
    "examination": "חקירת עדים",
    "arguments": "הצגת טענות",
    "cross": "חקירה נגדית",
    "closing": "סיכומים",
    "ruling": "גזר דין",
    "judgment": "פסק דין",
}

SPEAKER_STYLE = {
    "judge":    ("🔵", "#1a3a6b", "שופט"),
    "attorney": ("🔴", "#6b1a1a", "עו\"ד"),
    "user":     ("⚪", "#3a3a3a", "אתה"),
}


def _render_message(msg: dict):
    role = msg.get("role", "user")
    emoji, color, label = SPEAKER_STYLE.get(role, SPEAKER_STYLE["user"])
    st.markdown(
        f"""<div style="background:{color}22; border-right:4px solid {color};
        padding:10px 14px; margin:6px 0; border-radius:6px; direction:rtl;">
        <strong>{emoji} {label}:</strong> {msg["content"]}</div>""",
        unsafe_allow_html=True,
    )


def render():
    phase = st.session_state.get("phase", "opening")
    case = st.session_state.get("case", {})
    personas = st.session_state.get("personas", {})
    messages = st.session_state.get("messages", [])

    judge_display = case.get("judge_name") or "שופט"
    phase_label = PHASE_LABELS.get(phase, phase)
    st.subheader(f"שלב: {phase_label} | שופט: {judge_display}")
    st.markdown("---")

    for msg in messages:
        _render_message(msg)

    st.markdown("---")
    user_input = st.text_area("הטענה שלך:", key="user_input_area", height=100)

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        if st.button("שלח ▶", type="primary"):
            if user_input.strip():
                messages.append({"role": "user", "content": user_input.strip()})
                result = send_message(
                    user_input=user_input.strip(),
                    messages=messages,
                    phase=phase,
                    case=case,
                    personas=personas,
                )
                messages.append(result["judge_response"])
                messages.append(result["attorney_response"])
                st.session_state["messages"] = messages
                st.session_state["phase"] = result["new_phase"]
                st.rerun()

    with col2:
        if st.button("סיים דיון 🔚"):
            debrief = end_session(messages)
            st.session_state["debrief"] = debrief
            st.session_state["screen"] = "debrief"
            st.rerun()

    with col3:
        if st.button("התחל מחדש 🔄"):
            for key in ["case", "personas", "phase", "messages", "debrief"]:
                st.session_state.pop(key, None)
            st.session_state["screen"] = "setup"
            st.rerun()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_chat_view.py -v`

Expected: 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add ui/chat_view.py tests/test_chat_view.py
git commit -m "feat: chat view with message display, send, end session, and reset"
```

---

## Task 6: Full Test Suite + Manual Smoke Test

**Files:**
- No new files — run everything together

- [ ] **Step 1: Run the full test suite**

Run: `pytest tests/ -v`

Expected: All tests PASS. If any fail, fix before continuing.

- [ ] **Step 2: Start the app**

Run: `streamlit run app.py`

Expected: Browser opens at `http://localhost:8501` with a Hebrew RTL page showing the setup form.

- [ ] **Step 3: Verify setup form manually**

In the browser:
1. Select "פלילי"
2. Fill in parties, charges, evidence fields
3. Click "בחן אותי! ⚖️"
4. Verify the chat screen loads with a blue judge opening message and the phase header "שלב: פתיחה"

- [ ] **Step 4: Verify chat interaction manually**

In the browser:
1. Type something in the text area
2. Click "שלח ▶"
3. Verify your message appears (⚪), then a blue judge stub response and red attorney stub response appear below it
4. Click "סיים דיון 🔚"
5. Verify the screen shows "טוען דוח מאמן... (בקרוב)"
6. Navigate back (or refresh), click "התחל מחדש 🔄" — verify it returns to the setup form

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: complete frontend implementation with stubs — ready for backend integration"
```

---

## Integration Notes for Backend Handoff

When Person 1 is ready to replace the stubs in `core/orchestrator.py`:

- `start_session(case)` must still return `{phase: str, personas: dict, opening_message: dict}` — the `opening_message` dict must have `role` and `content` keys
- `send_message(...)` must still return `{judge_response: dict, attorney_response: dict, new_phase: str}` — both response dicts must have `role` and `content` keys
- `end_session(messages)` must still return `{scores: dict, strengths: list, weaknesses: list, errors: list, recommendations: list}`
- **No UI code changes needed** as long as these return shapes are preserved

When Person 4 adds `ui/debrief_view.py`, update `app.py`:

```python
elif screen == "debrief":
    from ui.debrief_view import render
    render()
```
