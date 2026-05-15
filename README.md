# מתמחה בבית המשפט — Court Practice Simulator

**AI-powered Hebrew courtroom simulation for Israeli law practitioners**

Upload real case documents, face a senior judge and opposing counsel powered by Claude Sonnet, and receive a structured performance debrief — all locally, in fluent legal Hebrew.

---

## What It Does

1. **Upload** your כתב תביעה/כתב אישום and כתב הגנה
2. **Practice** — argue your case against a simulated judge and opposing attorney in real Hebrew dialogue
3. **Debrief** — get a scored post-session analysis with actionable feedback

---

## Features

### ⚖️ Realistic Simulation
- Two AI agents: **Judge** (🔵) and **Opposing Attorney** (🔴) with distinct Hebrew voices
- Document-grounded — agents reason strictly from your uploaded case files, no hallucinated facts
- Phase-by-phase flow matching Israeli procedure:
  - **Criminal**: Opening → Evidence → Witness Examination → Closing → Ruling
  - **Civil**: Opening → Arguments → Cross-Examination → Closing → Judgment
- Auto-phase advancement every 4 exchanges

### 📄 Document Intelligence
- Accepts `.txt`, `.pdf`, `.docx` for both pleadings
- One-shot document analysis at session start: identifies key claims, evidence gaps, contradictions, and procedural issues
- RAG over `חוק סדר הדין הפלילי`, `תקנות סדר הדין האזרחי`, and related statutes (ChromaDB + multilingual embeddings)

### 📊 Coach Debrief
Scores your performance across 5 dimensions (1–10):

| Dimension | Hebrew |
|---|---|
| Persuasiveness | שכנוע |
| Legal Mastery | שליטה בחוק |
| Evidence Management | ניהול ראיות |
| Challenge Response | תגובה לאתגרים |
| Procedure & Order | סדרה ונוהל |

Includes: strengths, weaknesses, procedural errors, and top recommendations.

### ⚡ Quick Mode
Toggle **משפט קצר** at setup for 50–100 word responses — fast practice runs.

### 🔄 Optimistic UI
Your message appears instantly on send; agent responses stream token-by-token into styled bubbles.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit 1.40+ (RTL Hebrew, `st.form`, `write_stream`) |
| AI Model | Claude Sonnet 4.5 via OpenRouter |
| HTTP | httpx with streaming (`client.stream()`) |
| RAG | ChromaDB + `paraphrase-multilingual-MiniLM-L12-v2` |
| Document parsing | pypdf, pdfplumber, python-docx |
| Data validation | Pydantic v2 |

---

## Project Structure

```
├── app.py                   # Entry point, CSS, screen routing
├── config.py                # API config, phase definitions, enums
├── requirements.txt
│
├── core/
│   ├── openrouter.py        # httpx API client + streaming generator
│   ├── orchestrator.py      # Phase state machine, start_session(), send_message()
│   ├── prompts.py           # Hebrew system prompts (judge, attorney)
│   ├── document_analyzer.py # One-shot LLM analysis of uploaded pleadings
│   └── rag/
│       └── law_rag.py       # ChromaDB vector index over Israeli law text
│
├── agents/
│   ├── judge.py             # JudgeAgent — speak(), speak_stream_chunks()
│   ├── attorney.py          # AttorneyAgent — speak(), speak_stream_chunks()
│   ├── coach.py             # CoachAgent — post-session DebriefReport (Pydantic)
│   └── research.py          # Persona research via Firecrawl (optional)
│
├── ui/
│   ├── setup_form.py        # Upload form, case type, quick mode toggle
│   ├── chat_view.py         # Streaming chat interface
│   └── debrief_view.py      # Scored debrief cards
│
├── data/
│   └── session_store.py     # Local session persistence
│
└── Assets/
    ├── IsraelyLaw.txt        # Israeli law corpus for RAG
    └── Lawsuits/             # Sample case documents
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- OpenRouter API key — [openrouter.ai](https://openrouter.ai)

### Installation

```bash
# 1. Clone
git clone <repo>
cd HackathonBIU

# 2. Virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 3. Dependencies
pip install -r requirements.txt

# 4. Environment
cp .env.example .env
# add OPENROUTER_API_KEY=sk-or-...
```

### Run

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

### Build the Law Index (first run only)

```bash
python build_law_index.py
```

This indexes `Assets/IsraelyLaw.txt` into ChromaDB at `.rag_cache/`. Skip if you don't have the corpus — the app proceeds without RAG context.

---

## Usage

### 1. Setup
- Choose **פלילי** (Criminal) or **אזרחי** (Civil)
- Select your side: **הגנה** (Defense) or **תביעה** (Prosecution)
- Upload כתב תביעה/אישום and כתב הגנה
- Optionally toggle ⚡ **משפט קצר** for quick mode
- Click **בחן אותי! ⚖️**

### 2. Simulation
- The judge opens with formal remarks
- Type your argument in the text area and click **שלח ▶**
- Your message appears immediately; the judge streams a response, then the attorney reacts, then the judge follows up
- Proceed through phases — they advance automatically
- Click **סיים דיון 🔚** when ready for the debrief

### 3. Debrief
- View overall score and per-dimension breakdown
- Read strengths, weaknesses, procedural issues, and recommendations
- Click **התחל מחדש 🔄** for another session

---

## Legal Framework

### Anti-Hallucination
Agents are grounded in two ways:
1. **Raw document text** — both pleadings (up to 6 000 chars each) are injected verbatim into every system prompt with a strict "cite only what is in the documents" instruction
2. **Document analysis** — a structured LLM analysis of claims, evidence, and contradictions is produced once at session start and injected into all subsequent prompts

Agents never invent case numbers, statute sections, or judge names.

### Statutes Referenced
- חוק סדר הדין הפלילי [נוסח משולב], תשמ"ב-1982
- חוק העונשין, תשל"ז-1977
- פקודת הראיות [נוסח חדש], תשל"א-1971
- תקנות סדר הדין האזרחי, תשע"ט-2018
- חוק החוזים (חלק כללי), תשל"ג-1973
- פקודת הנזיקין [נוסח חדש]

---

## Known Limitations

- **Streaming requires OpenRouter** — the app does not support local/offline models
- **RAG index** must be built manually on first run (`build_law_index.py`)
- **Coach agent** uses the same Claude Sonnet model and consumes ~4K tokens per debrief; very long sessions (40+ exchanges) are trimmed to the last 40 messages

---

**BIU Hackathon 2026 · מתמחה בבית המשפט**
