"""
Session Orchestrator - Phase State Machine
Manages hearing phases, routes messages to correct agents, tracks objections
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from config import CaseType, CRIMINAL_PHASES, CIVIL_PHASES, PHASE_NAMES_HE


class PhaseTransitionError(Exception):
    """Raised when an invalid phase transition is attempted."""

    pass


@dataclass
class SessionState:
    """Represents the state of a court simulation session."""

    session_id: str
    case_type: CaseType
    current_phase: str
    judge_name: Optional[str] = None
    attorney_name: Optional[str] = None
    judge_persona: Dict[str, Any] = field(default_factory=dict)
    attorney_persona: Dict[str, Any] = field(default_factory=dict)
    case_facts: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    objections_count: int = 0
    rulings_count: int = 0
    is_complete: bool = False

    def get_phases(self) -> List[str]:
        """Get the phase list for this case type."""
        return CRIMINAL_PHASES if self.case_type == CaseType.CRIMINAL else CIVIL_PHASES

    def get_current_phase_name_he(self) -> str:
        """Get the Hebrew name of the current phase."""
        return PHASE_NAMES_HE.get(self.current_phase, self.current_phase)

    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history."""
        self.conversation_history.append(
            {"role": role, "content": content, "phase": self.current_phase}
        )

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get all messages in conversation."""
        return self.conversation_history

    def get_conversation_by_phase(self, phase: str) -> List[Dict[str, Any]]:
        """Get all messages from a specific phase."""
        return [msg for msg in self.conversation_history if msg.get("phase") == phase]

    def get_last_n_messages(self, n: int) -> List[Dict[str, Any]]:
        """Get the last N messages (for context window)."""
        return self.conversation_history[-n:]


class Orchestrator:
    """Manages session state and phase transitions."""

    def __init__(self, session_id: str, case_type: CaseType):
        self.session_id = session_id
        self.case_type = case_type
        self.phases = (
            CRIMINAL_PHASES if case_type == CaseType.CRIMINAL else CIVIL_PHASES
        )
        self.state = SessionState(
            session_id=session_id,
            case_type=case_type,
            current_phase=self.phases[0],  # Start at "setup"
        )

    def set_judge(self, name: str, persona: dict) -> None:
        """Set judge name and persona data."""
        self.state.judge_name = name
        self.state.judge_persona = persona

    def set_attorney(self, name: str, persona: dict) -> None:
        """Set opposing attorney name and persona data."""
        self.state.attorney_name = name
        self.state.attorney_persona = persona

    def set_case_facts(self, facts: dict) -> None:
        """Set case facts from the setup form."""
        self.state.case_facts = facts

    def advance_phase(self) -> str:
        """
        Advance to the next phase.

        Returns:
            The new phase name

        Raises:
            PhaseTransitionError: If already at the final phase
        """
        current_index = self.phases.index(self.state.current_phase)
        if current_index >= len(self.phases) - 1:
            raise PhaseTransitionError(
                f"Cannot advance from final phase: {self.state.current_phase}"
            )

        new_phase = self.phases[current_index + 1]
        self.state.current_phase = new_phase
        return new_phase

    def can_advance_phase(self) -> bool:
        """Check if we can advance to the next phase."""
        current_index = self.phases.index(self.state.current_phase)
        return current_index < len(self.phases) - 1

    def go_to_phase(self, phase: str) -> None:
        """
        Jump to a specific phase.

        Raises:
            ValueError: If phase is not valid for this case type
        """
        if phase not in self.phases:
            raise ValueError(
                f"Invalid phase '{phase}' for case type {self.case_type.value}"
            )
        self.state.current_phase = phase

    def get_state(self) -> SessionState:
        """Get the current session state."""
        return self.state

    def add_conversation_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.state.add_message(role, content)

    def get_context_window(self, max_messages: int = 10) -> List[Dict[str, Any]]:
        """
        Get the recent conversation for context (to avoid token bloat).

        Returns:
            List of recent messages (max_messages count)
        """
        return self.state.get_last_n_messages(max_messages)

    def record_objection(self) -> None:
        """Record that an objection was raised."""
        self.state.objections_count += 1

    def record_ruling(self) -> None:
        """Record that the judge made a ruling."""
        self.state.rulings_count += 1

    def mark_complete(self) -> None:
        """Mark the session as complete."""
        self.state.is_complete = True

    def get_system_prompt_context(self) -> Dict[str, Any]:
        """
        Build context dict for injecting into agent system prompts.

        Returns:
            Dict with case info, personas, phase info
        """
        return {
            "case_type": self.case_type.value,
            "case_facts": self.state.case_facts,
            "judge_name": self.state.judge_name or "שופט בכיר",
            "judge_persona": self.state.judge_persona,
            "attorney_name": self.state.attorney_name or "עורך דין בכיר",
            "attorney_persona": self.state.attorney_persona,
            "current_phase": self.state.current_phase,
            "current_phase_he": self.get_phase_name_he(),
            "phases_remaining": len(self.phases)
            - self.phases.index(self.state.current_phase),
        }

    def get_phase_name_he(self) -> str:
        """Get Hebrew name of current phase."""
        return self.state.get_current_phase_name_he()


# ── Session-level convenience functions (used by Streamlit UI) ────────────────
# These wrap the Orchestrator class using st.session_state for persistence
# across Streamlit reruns. The Orchestrator class itself is not modified.

def start_session(case: dict) -> dict:
    """
    Initialise a new court session from setup form data.

    Returns dict with keys: personas, phase, opening_message
    """
    import uuid
    import streamlit as st
    from agents.judge import JudgeAgent
    from agents.attorney import AttorneyAgent
    from config import (
        CaseType, DEFAULT_JUDGE_STYLE, DEFAULT_ATTORNEY_STYLE
    )

    case_type = CaseType.CRIMINAL if case.get("type") == "criminal" else CaseType.CIVIL

    orch = Orchestrator(session_id=str(uuid.uuid4()), case_type=case_type)
    orch.set_case_facts({
        "parties": case.get("parties", ""),
        "charges": case.get("charges", ""),
        "evidence": case.get("evidence", ""),
    })

    judge_name = case.get("judge_name") or "שופט בכיר"
    attorney_name = case.get("attorney_name") or "עורך דין בכיר"
    orch.set_judge(judge_name, DEFAULT_JUDGE_STYLE)
    orch.set_attorney(attorney_name, DEFAULT_ATTORNEY_STYLE)

    # Advance from "setup" → "opening"
    orch.advance_phase()

    judge = JudgeAgent(orch)
    attorney = AttorneyAgent(orch)

    st.session_state["_orchestrator"] = orch
    st.session_state["_judge"] = judge
    st.session_state["_attorney"] = attorney
    st.session_state["_msg_count"] = 0

    opening_text = judge.opening_remarks()

    return {
        "personas": {
            "judge": {"name": judge_name},
            "attorney": {"name": attorney_name},
        },
        "phase": orch.get_state().current_phase,
        "opening_message": {
            "role": "judge",
            "content": opening_text,
            "speaker": judge_name,
        },
    }


def send_message(
    user_input: str,
    messages: list,
    phase: str,
    case: dict,
    personas: dict,
) -> dict:
    """
    Process lawyer's message: judge responds, then attorney responds.

    Returns dict with keys: judge_response, attorney_response, new_phase
    """
    import streamlit as st

    orch: Orchestrator = st.session_state.get("_orchestrator")
    judge = st.session_state.get("_judge")
    attorney = st.session_state.get("_attorney")

    if not orch or not judge or not attorney:
        raise RuntimeError("Session not initialised — call start_session first.")

    judge_text = judge.speak(lawyer_message=user_input)
    attorney_text = attorney.speak()

    # Auto-advance phase every 4 lawyer messages, but never into "debrief"
    count = st.session_state.get("_msg_count", 0) + 1
    st.session_state["_msg_count"] = count

    if count % 4 == 0 and orch.can_advance_phase():
        next_phase = orch.get_state().get_phases()[
            orch.get_state().get_phases().index(orch.get_state().current_phase) + 1
        ]
        if next_phase != "debrief":
            orch.advance_phase()

    judge_name = personas.get("judge", {}).get("name", "כב׳ השופט")
    attorney_name = personas.get("attorney", {}).get("name", 'עו"ד שכנגד')

    return {
        "judge_response": {
            "role": "judge",
            "content": judge_text,
            "speaker": judge_name,
        },
        "attorney_response": {
            "role": "attorney",
            "content": attorney_text,
            "speaker": attorney_name,
        },
        "new_phase": orch.get_state().current_phase,
    }


def end_session(messages: list):
    """
    End the session and return a DebriefReport from the coach agent.

    Maps UI message roles to coach transcript format, then calls analyze_session.
    """
    import streamlit as st
    from agents.coach import analyze_session

    orch: Orchestrator = st.session_state.get("_orchestrator")
    case_type = "פלילי"
    if orch:
        from config import CaseType
        case_type = "פלילי" if orch.case_type == CaseType.CRIMINAL else "אזרחי"
        orch.mark_complete()

    # Map "user" → "lawyer" so the coach prompt recognises the role
    role_map = {"user": "lawyer", "judge": "judge", "attorney": "attorney"}
    transcript = [
        {"role": role_map.get(m.get("role", "user"), "lawyer"),
         "content": m.get("content", "")}
        for m in messages
    ]

    return analyze_session(transcript, case_type)
