# מתמחה בבית המשפט — Court Practice Simulator

A Hebrew-language AI-powered court simulation system for Israeli lawyers to rehearse court proceedings.

**מתמחה בבית המשפט** (Court Practice Simulator) — BIU Hackathon 2026

## Overview

This system allows lawyers to:
1. **Set up a case** — provide case details, charges/claims, evidence, and optional judge/attorney names
2. **Simulate a hearing** — interact with two AI agents (Judge and Opposing Attorney) in realistic Hebrew dialogue
3. **Receive feedback** — get a structured debrief report analyzing strengths, weaknesses, and procedural errors

## Features

### 🔵 Judge Agent
- Conducts the hearing in formal Hebrew
- Asks sharp questions about evidence admissibility
- Rules on objections based on Israeli law
- Manages phase transitions (opening → evidence → closing → ruling)

### 🔴 Opposing Attorney Agent
- Presents counter-arguments
- Raises objections (hearsay, lack of foundation, etc.)
- Conducts cross-examination
- Challenges evidence based on Israeli procedural law

### 📊 Coach Agent (Post-Session Analysis)
- Analyzes full session transcript
- Scores performance across 5 dimensions:
  - **שכנוע** (Persuasiveness)
  - **שליטה בחוק** (Legal Mastery)
  - **ניהול ראיות** (Evidence Management)
  - **תגובה לאתגרים** (Challenge Response)
  - **סדרה ונוהל** (Procedure & Order)
- Provides actionable recommendations

### 🔍 Research Agent (Optional)
- Searches Hebrew legal databases for judge/attorney information
- Builds realistic personas based on real individuals
- Falls back to elite default personas if no info found

## Tech Stack

- **Backend**: Python with LangChain-ready design
- **AI Model**: Claude Sonnet 4.5 (via OpenRouter API)
- **Frontend**: Streamlit with Hebrew RTL support
- **State Management**: Streamlit session state + Orchestrator pattern

## Project Structure

```
Hackathon/
├── app.py                    # Streamlit main entry point
├── config.py                 # Configuration, enums, legal references
├── requirements.txt          # Python dependencies
├── .env                      # API keys (DO NOT COMMIT)
├── .env.example              # Template for .env
│
├── core/
│   ├── openrouter.py        # OpenRouter API client
│   ├── orchestrator.py      # Session state machine (phases)
│   ├── prompts.py           # All Hebrew system prompts
│   └── __init__.py
│
├── agents/
│   ├── judge.py             # Judge agent logic
│   ├── attorney.py          # Opposing attorney agent logic
│   ├── coach.py             # Post-session analysis (stub)
│   ├── research.py          # Judge/attorney research (stub)
│   └── __init__.py
│
├── ui/
│   ├── setup_form.py        # Case setup form component
│   ├── chat_view.py         # Simulation chat interface
│   ├── debrief_view.py      # Debrief report component
│   └── __init__.py
│
├── README.md                # This file
└── PLAN.md                  # Implementation plan
```

## Getting Started

### Prerequisites

- Python 3.9+
- OpenRouter API key (https://openrouter.io)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repo>
   cd HackathonBIU
   ```

2. **Create a Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENROUTER_API_KEY
   ```

### Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage Workflow

### 1. Home Page
- Choose case type: **Criminal (פלילי)** or **Civil (אזרחי)**

### 2. Setup Form
- Enter case parties, charges/claims, evidence, and your main argument
- Optionally provide judge and attorney names for persona research
- Click "התחל דיון" (Start Hearing)

### 3. Simulation
- Judge opens with formal remarks
- You present your argument
- Attorney objects (raises procedural/evidence challenges)
- Judge rules on objections
- Proceed through phases: opening → evidence → closing → ruling
- Use buttons to:
  - Submit response/argument
  - Skip to next phase
  - End hearing when complete

### 4. Debrief Report
- See your overall score (1-10)
- Review breakdown by 5 performance dimensions
- Read detailed feedback: strengths, weaknesses, procedural errors
- Get recommendations for improvement

## Legal Framework

### Criminal Cases (פלילי)
- **Primary Law**: חוק סדר הדין הפלילי [נוסח משולב], תשמ"ב-1982
- **Penal Code**: חוק העונשין, תשל"ז-1977
- **Evidence**: פקודת הראיות [נוסח חדש], תשל"א-1971
- **Phases**: Opening → Evidence Presentation → Witness Examination → Closing → Ruling

### Civil Cases (אזרחי)
- **Primary Law**: תקנות סדר הדין האזרחי, תשע"ט-2018
- **Contract Law**: חוק החוזים (חלק כללי), תשל"ג-1973
- **Torts**: פקודת הנזיקין [נוסח חדש]
- **Phases**: Opening → Arguments → Cross-Examination → Closing → Judgment

## Key Design Decisions

### Anti-Hallucination Rules
- Agents **only** cite real Israeli statutes and Supreme Court precedents
- When uncertain, agents say: "בהתאם לעקרונות הכלליים של הדין הישראלי"
- Never invent case names, docket numbers, or statute sections

### Persona Injection
- Judge and attorney personas are injected into their system prompts
- If research finds real information → use actual persona
- If not found → use elite default persona (e.g., Supreme Court judge characteristics)

### Phase State Machine
- Orchestrator manages strict phase transitions
- Each phase has specific instructions for judge/attorney behavior
- Lawyer can manually skip phases or let agents advance

### Context Window Management
- Only last 10 messages included per API call (save tokens)
- Full transcript stored in orchestrator for coach analysis
- Reduces hallucination by keeping context focused

## API Costs

- Model: Claude Sonnet 4.5 (~$3 per 1M tokens)
- Average session: ~10K tokens = ~$0.03
- Budget: $50 = ~1,600+ sessions

## Team Responsibilities (12-Hour Hackathon)

### Person 1 — CS Masters → **Architect + Core Agents** (YOU)
- ✅ Hours 1–3: Project skeleton, config, orchestrator, prompts
- ✅ Hours 3–7: Judge & Attorney agents
- ✅ Hours 7–10: Streamlit integration
- ⏳ Hours 10–12: Testing, refinement, bug fixes

### Person 2 — Comp Engineering → **Research Agent + DevOps**
- Setup environment, GitHub, `requirements.txt`
- Implement `agents/research.py` with Firecrawl search/scrape
- Connect research output to agent prompts
- Integration testing

### Person 3 — Data Engineering Student 1 → **Streamlit Frontend**
- Polish UI/RTL Hebrew styling
- Refine `ui/setup_form.py`, `ui/chat_view.py`
- Session reset, phase headers

### Person 4 — Data Engineering Student 2 → **Coach Agent + Evaluation**
- Implement `agents/coach.py` with transcript analysis
- Build benchmark scoring system (5 dimensions)
- Create `ui/debrief_view.py`
- Final docs and demo prep

## Current Status

### ✅ Completed
- [x] Project skeleton & configuration
- [x] OpenRouter API client
- [x] Orchestrator (phase state machine)
- [x] All Hebrew system prompts
- [x] Judge agent (full logic)
- [x] Attorney agent (full logic)
- [x] Streamlit app structure + navigation
- [x] UI components (setup, chat, debrief stubs)

### ⏳ In Progress
- [ ] Bug fixes and prompt refinement (Person 1)
- [ ] Research agent implementation (Person 2)
- [ ] Coach agent implementation (Person 4)
- [ ] UI polish and RTL fixes (Person 3)

### 🔄 TODO
- [ ] End-to-end testing with real case
- [ ] Integration of research agent into judge/attorney initialization
- [ ] Debrief report generation and display
- [ ] Session persistence (optional)
- [ ] Export to PDF/Excel

## Known Issues & Limitations

1. **Coach & Research Agents**: Currently stubs — Person 2 and Person 4 to implement
2. **Hebrew Rendering**: Streamlit RTL support added, but may need tweaking
3. **Model Rate Limiting**: OpenRouter may rate-limit concurrent requests
4. **Context Window**: Some sessions may exceed token limits on very long transcripts

## Future Enhancements

- Multi-round conversation with same agents
- Session history and progress tracking
- Comparative scoring across sessions
- Export to PDF/PowerPoint
- Video/audio support
- Integration with Israeli legal databases

## Support

For questions or issues:
1. Check [PLAN.md](PLAN.md) for architecture details
2. Review [config.py](config.py) for available settings
3. Check agent system prompts in [core/prompts.py](core/prompts.py)

---

**Made with ❤️ for Israeli lawyers learning to master court proceedings**

BIU Hackathon 2026 | מתמחה בבית המשפט
