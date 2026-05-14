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
