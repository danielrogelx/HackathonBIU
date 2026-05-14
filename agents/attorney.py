"""
Opposing Attorney Agent
Simulates the opposing counsel in the court hearing
"""

from typing import Iterator, Optional, List, Dict, Union
from core.openrouter import chat, chat_stream
from core.orchestrator import Orchestrator
from core.prompts import get_attorney_system_prompt
from config import CaseType


class AttorneyAgent:
    """Manages interactions with the Opposing Attorney in the simulation."""

    def __init__(self, orchestrator: Orchestrator):
        """
        Initialize the Attorney agent.

        Args:
            orchestrator: The session orchestrator managing state
        """
        self.orchestrator = orchestrator
        self.conversation_history = []

    def _build_system_prompt(self) -> str:
        """Build the attorney's system prompt with current context."""
        state = self.orchestrator.get_state()
        return get_attorney_system_prompt(
            case_type=state.case_type,
            attorney_name=state.attorney_name or "עורך דין בכיר",
            attorney_persona=state.attorney_persona,
            case_facts=state.case_facts,
            current_phase=state.current_phase,
        )

    def _get_context_messages(self, max_context: int = 10) -> List[Dict]:
        """
        Get recent conversation context for API call.

        Includes messages from judge and lawyer, but not attorney's own reasoning.

        Args:
            max_context: Maximum number of recent messages to include

        Returns:
            List of message dicts for API
        """
        context = self.orchestrator.get_context_window(max_context)
        # Map internal roles to OpenRouter API roles (user / assistant only)
        role_map = {"lawyer": "user", "judge": "assistant", "attorney": "assistant"}
        return [
            {
                "role": role_map.get(msg.get("role", "user"), "user"),
                "content": msg.get("content", ""),
            }
            for msg in context
        ]

    def speak(
        self,
        lawyer_message: Optional[str] = None,
        stream: bool = False,
    ) -> Union[str, Iterator[str]]:
        """
        Generate the attorney's response to the lawyer.

        This is called when:
        1. After the lawyer presents arguments
        2. During cross-examination of the lawyer's witnesses
        3. In response to judge requests

        Args:
            lawyer_message: The message from the lawyer (if any)
            stream: Whether to stream the response

        Returns:
            Attorney's response (full string or iterator if streaming)
        """
        # Do NOT re-add the lawyer message — judge_agent.speak() already added it
        # to the orchestrator. Just read the current context.

        # Build messages for API call
        messages = self._get_context_messages()

        # Get attorney's response — force a direct reply regardless of phase
        system_prompt = (
            self._build_system_prompt()
            + "\n\nעכשיו תורך להגיב לטיעון האחרון של עורך הדין שמתאמן. "
            "הגב ישירות ובאופן תוקפני ומקצועי — אל תאמר שאתה צופה. "
            "תן תגובה קצרה וחדה של 2-4 משפטים בעברית."
        )

        if stream:
            full_response = "".join(
                chat_stream(messages=messages, system=system_prompt)
            )
        else:
            full_response = chat(messages=messages, system=system_prompt)
        self.conversation_history.append({"role": "attorney", "content": full_response})
        self.orchestrator.add_conversation_message("attorney", full_response)
        return full_response

    def object_to_evidence(
        self,
        evidence_description: str,
        stream: bool = False,
    ) -> Union[str, Iterator[str]]:
        """
        Attorney raises an objection to evidence presented by the lawyer.

        Common objections:
        - עדות שמיעה (Hearsay)
        - חוסר בסיס (Lack of foundation)
        - שיקול דעת לא שלם (Incomplete foundation)
        - הנחות שלא הוכחו (Unproven assumptions)

        Args:
            evidence_description: What evidence the lawyer presented
            stream: Whether to stream response

        Returns:
            Attorney's objection
        """
        # Add context about the evidence
        self.conversation_history.append(
            {"role": "lawyer", "content": f"הוכחה: {evidence_description}"}
        )
        self.orchestrator.add_conversation_message(
            "lawyer", f"הוכחה: {evidence_description}"
        )

        # Build a prompt that triggers objection
        system_with_objection = (
            self._build_system_prompt()
            + "\n\nעכשיו אתה מגיש התנגדות על בסיס חוק ישראלי. הגיד בבירור מה היא התנגדות ועל בסיס איזה חוק."
        )

        messages = self._get_context_messages()

        if stream:
            full_response = "".join(
                chat_stream(messages=messages, system=system_with_objection)
            )
        else:
            full_response = chat(messages=messages, system=system_with_objection)
            self.conversation_history.append({"role": "attorney", "content": response})
            self.orchestrator.add_conversation_message("attorney", response)
        return full_response

    def cross_examine(
        self,
        statement_to_challenge: str = "",
        stream: bool = False,
    ) -> Union[str, Iterator[str]]:
        """
        Attorney conducts cross-examination of the lawyer's claim.

        This is the key moment where the attorney challenges and probes
        the lawyer's statements to expose weaknesses.

        Args:
            statement_to_challenge: A specific statement the attorney wants to challenge
            stream: Whether to stream response

        Returns:
            Attorney's cross-examination question
        """
        system_with_cross = (
            self._build_system_prompt()
            + f"\n\nעכשיו אתה מנהל חקירה נגדית. {statement_to_challenge or ''}"
            + "\nשאל שאלה חדה שמערערת את התביעה. לא תן לו להימלט מתשובה ברורה."
        )

        messages = self._get_context_messages()

        if stream:
            full_response = "".join(
                chat_stream(messages=messages, system=system_with_cross)
            )
        else:
            full_response = chat(messages=messages, system=system_with_cross)
            self.conversation_history.append({"role": "attorney", "content": response})
            self.orchestrator.add_conversation_message("attorney", response)
        return full_response

    def deliver_counter_argument(
        self,
        stream: bool = False,
    ) -> Union[str, Iterator[str]]:
        """
        Attorney delivers their counter-argument to the lawyer's position.

        This is typically used during:
        - Opening (attorney's opening statement)
        - Arguments phase (attorney's full argument)
        - Closing (attorney's final argument)

        Args:
            stream: Whether to stream response

        Returns:
            Attorney's counter-argument
        """
        system_with_argument = (
            self._build_system_prompt()
            + "\n\nעכשיו אתה מחזיק טיעון שלם נגד התיק של עורך הדין. היה ברור, קצר, ומשכנע."
        )

        messages = self._get_context_messages()

        if stream:
            full_response = "".join(
                chat_stream(messages=messages, system=system_with_argument)
            )
        else:
            full_response = chat(messages=messages, system=system_with_argument)
            self.conversation_history.append({"role": "attorney", "content": response})
            self.orchestrator.add_conversation_message("attorney", response)
        return full_response

    def get_conversation_history(self) -> List[Dict]:
        """Get the full conversation history with the attorney."""
        return self.conversation_history

    def get_state_for_transcript(self) -> List[Dict]:
        """Get attorney messages in orchestrator format for transcript."""
        return [
            msg
            for msg in self.orchestrator.get_state().conversation_history
            if msg.get("role") in ("attorney", "lawyer", "judge")
        ]
