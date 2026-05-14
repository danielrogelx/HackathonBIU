# Data Engineering Student 1 — Streamlit Frontend Design
## HackAgents BIU 2026 | Court Practice Simulator (מתמחה בבית המשפט)

---

## Role

Person 3 on the team. Owns the Streamlit frontend: `app.py`, `ui/setup_form.py`, `ui/chat_view.py`, and the interface contract stubs in `core/orchestrator.py`. Person 4 owns `ui/debrief_view.py`.

---

## Approach

Component modules with a thin router (Option B). `app.py` is a ~25-line router. Each screen is a module exporting a single `render()` function. The interface contract lives in `core/orchestrator.py` as stubs — Person 1 replaces the stub bodies with real logic; UI call sites stay unchanged.

Streaming text output is a stretch goal. Start with full-response display; add streaming only if time permits.

---

## Session State

All state lives in `st.session_state`. No extra classes.

| Key | Type | Description |
|---|---|---|
| `screen` | `str` | Current view: `"setup"` / `"chat"` / `"debrief"` |
| `case` | `dict` | Form data: type, parties, charges, evidence, judge_name, attorney_name |
| `personas` | `dict` | Research agent output: judge persona, attorney persona |
| `phase` | `str` | Current hearing phase (e.g. `"opening"`, `"evidence"`) |
| `messages` | `list[dict]` | Chat history: `{role, content, speaker}` — also passed directly to coach agent |

Screen transitions: set `st.session_state.screen` then call `st.rerun()`.

---

## Interface Contract (`core/orchestrator.py` stubs)

These four functions are what the UI calls. Person 1 implements the bodies.

```python
def start_session(case: dict) -> dict:
    """Returns {phase, personas, opening_message}"""
    return {
        "phase": "opening",
        "personas": {"judge": "שופט ברירת מחדל", "attorney": "עו\"ד ברירת מחדל"},
        "opening_message": {"role": "judge", "content": "הדיון נפתח. עורך הדין, אנא הציג את טיעוניכם."}
    }

def send_message(user_input: str, messages: list, phase: str, case: dict, personas: dict) -> dict:
    """Returns {judge_response, attorney_response, new_phase}"""
    return {
        "judge_response": {"role": "judge", "content": f"[stub] קיבלתי: {user_input}"},
        "attorney_response": {"role": "attorney", "content": "[stub] אני מתנגד!"},
        "new_phase": phase,
    }

def end_session(messages: list) -> dict:
    """Returns debrief dict: {scores, strengths, weaknesses, errors, recommendations}"""
    return {"scores": {}, "strengths": [], "weaknesses": [], "errors": [], "recommendations": []}

def reset_session() -> None:
    """Clears all session state keys and returns to setup screen."""
    for key in ["case", "personas", "phase", "messages", "transcript"]:
        if key in st.session_state:
            del st.session_state[key]
    st.session_state.screen = "setup"
```

---

## `app.py`

- Injects Hebrew RTL CSS via `st.markdown(..., unsafe_allow_html=True)`
- Reads `st.session_state.get("screen", "setup")`
- Routes to the matching `render()` function

```python
st.markdown('<style>body, .stApp { direction: rtl; text-align: right; }</style>', unsafe_allow_html=True)

screen = st.session_state.get("screen", "setup")
if screen == "setup":
    from ui.setup_form import render; render()
elif screen == "chat":
    from ui.chat_view import render; render()
elif screen == "debrief":
    from ui.debrief_view import render; render()
```

---

## `ui/setup_form.py`

Fields:
- Case type radio: `פלילי` / `אזרחי`
- Text input: parties (הצדדים)
- Text input: charges/claim (האישום / התביעה)
- Text area: key evidence (ראיות מרכזיות)
- Text input (optional): judge name (שם השופט)
- Text input (optional): opposing attorney name (שם עו"ד הצד שכנגד)

On "בחן אותי!" button click:
1. Call `start_session(case)` from `core/orchestrator`
2. Write returned `phase`, `personas`, `opening_message` to session state
3. Append `opening_message` to `messages`
4. Set `screen = "chat"` and `st.rerun()`

---

## `ui/chat_view.py`

Three zones:

**1. Phase header**
```
st.subheader(f"שלב: {phase_label} | שופט: {judge_name}")
```
`phase_label` maps phase keys to Hebrew display names. Define this dict locally in `chat_view.py` to avoid cross-file dependency (e.g. `{"opening": "פתיחה", "evidence": "הצגת הוכחות", ...}`).

**2. Message display**
Loop over `st.session_state.messages`. Style each by `role`:
- `"judge"` → blue box, prefix `🔵 שופט:`
- `"attorney"` → red box, prefix `🔴 עו"ד:`
- `"user"` → grey/white box, prefix `⚪ אתה:`

Use `st.markdown` with inline CSS for colored boxes.

**3. Input row**
- `st.text_area` for lawyer's input
- "שלח" button:
  1. Append user message to `messages`
  2. Call `send_message(...)`
  3. Append `judge_response` and `attorney_response` to `messages`
  4. Update `phase` if `new_phase` differs
  5. `st.rerun()`
- "סיים דיון" button:
  1. Call `end_session(messages)`
  2. Store debrief result in `st.session_state.debrief` (Person 4's `debrief_view.py` reads this key)
  3. Set `screen = "debrief"` and `st.rerun()`
- "התחל מחדש" (reset) button: calls `reset_session()`

---

## Build Order

1. `core/orchestrator.py` stubs (15 min) — unblocks everything
2. `app.py` router + RTL CSS (20 min)
3. `ui/setup_form.py` (45 min)
4. `ui/chat_view.py` message display (45 min)
5. `ui/chat_view.py` input + send logic (45 min)
6. End-to-end test with stubs (30 min)
7. Polish: RTL fixes, phase labels, reset button, error states (remaining time)
8. Swap stubs for real backend when Person 1 is ready

---

## Files Owned by Person 3

```
app.py
core/orchestrator.py       ← stubs only; Person 1 fills bodies
ui/__init__.py
ui/setup_form.py
ui/chat_view.py
```

## Files NOT Owned by Person 3

```
ui/debrief_view.py         ← Person 4
agents/                    ← Person 1 + Person 2
core/openrouter.py         ← Person 1
core/prompts.py            ← Person 1
```
