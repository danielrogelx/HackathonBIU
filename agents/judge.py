"""
Judge Agent
Simulates a senior Israeli judge conducting the hearing
"""

from typing import Iterator, Optional, List, Dict, Union
from core.openrouter import chat, chat_stream
from core.orchestrator import Orchestrator
from core.prompts import get_judge_system_prompt
from config import CaseType


class JudgeAgent:
    """Manages interactions with the Judge in the simulation."""

    def __init__(self, orchestrator: Orchestrator):
        """
        Initialize the Judge agent.

        Args:
            orchestrator: The session orchestrator managing state
        """
        self.orchestrator = orchestrator
        self.conversation_history = []

    def _build_system_prompt(self) -> str:
        """Build the judge's system prompt with current context."""
        import streamlit as st
        state = self.orchestrator.get_state()
        return get_judge_system_prompt(
            case_type=state.case_type,
            judge_name=state.judge_name or "שופט בכיר",
            judge_persona=state.judge_persona,
            case_facts=state.case_facts,
            current_phase=state.current_phase,
            document_analysis=st.session_state.get("_document_analysis", ""),
            law_context=st.session_state.get("_law_context", ""),
            user_side=st.session_state.get("_user_side", "defense"),
        )

    def _get_context_messages(self, max_context: int = 10) -> List[Dict]:
        """
        Get recent conversation context for API call.

        Filters to only get messages relevant to judge (not attorney private)
        and limits to recent context to save tokens.

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
        Generate the judge's response to the lawyer.

        This is called when:
        1. The hearing is starting (opening remarks)
        2. After the lawyer speaks
        3. After attorney objects

        Args:
            lawyer_message: The message from the lawyer (if any)
            stream: Whether to stream the response

        Returns:
            Judge's response (full string or iterator if streaming)
        """
        # Add lawyer message to history if provided
        if lawyer_message:
            self.conversation_history.append(
                {"role": "lawyer", "content": lawyer_message}
            )
            self.orchestrator.add_conversation_message("lawyer", lawyer_message)

        # Build messages for API call
        messages = self._get_context_messages()

        # Get judge's response
        system_prompt = self._build_system_prompt()

        if stream:
            full_response = "".join(
                chat_stream(messages=messages, system=system_prompt)
            )
            self.conversation_history.append(
                {"role": "judge", "content": full_response}
            )
            self.orchestrator.add_conversation_message("judge", full_response)
            return full_response
        else:
            response = chat(
                messages=messages,
                system=system_prompt,
            )
            self.conversation_history.append({"role": "judge", "content": response})
            self.orchestrator.add_conversation_message("judge", response)
            return response

    def opening_remarks(self, stream: bool = False) -> Union[str, Iterator[str]]:
        """
        Judge opens the hearing with formal remarks.

        Called at the start of the simulation.

        Returns:
            Judge's opening remarks
        """
        # Build a prompt that triggers opening remarks specifically
        system_with_opening = (
            self._build_system_prompt()
            + "\n\n׳¢׳›׳©׳™׳• ׳׳×׳” ׳׳•׳¦׳™׳ ׳׳× ׳”׳“׳™׳•׳ ׳׳“׳¨׳ ׳¢׳ ׳”׳¢׳¨׳•׳× ׳₪׳×׳™׳—׳” ׳₪׳•׳¨׳׳׳™׳•׳× ׳‘׳¢׳‘׳¨׳™׳×."
        )

        messages = []  # No prior context for opening

        if stream:
            full_response = "".join(
                chat_stream(messages=messages, system=system_with_opening)
            )
        else:
            full_response = chat(messages=messages, system=system_with_opening)
        self.conversation_history.append({"role": "judge", "content": full_response})
        self.orchestrator.add_conversation_message("judge", full_response)
        return full_response

    def rule_on_objection(
        self,
        objection_text: str,
        stream: bool = False,
    ) -> Union[str, Iterator[str]]:
        """
        Judge rules on an objection from the opposing attorney.

        Args:
            objection_text: The objection raised
            stream: Whether to stream response

        Returns:
            Judge's ruling on the objection
        """
        self.orchestrator.record_objection()

        # Add objection to history
        self.conversation_history.append(
            {"role": "attorney", "content": f"׳”׳×׳ ׳’׳“׳•׳×: {objection_text}"}
        )
        self.orchestrator.add_conversation_message(
            "attorney", f"׳”׳×׳ ׳’׳“׳•׳×: {objection_text}"
        )

        # Build a prompt that triggers ruling
        system_with_ruling = (
            self._build_system_prompt()
            + "\n\n׳¢׳›׳©׳™׳• ׳׳×׳” ׳׳—׳׳™׳˜ ׳¢׳ ׳”׳×׳ ׳’׳“׳•׳× ׳©׳ ׳×׳’׳“׳”. ׳׳׳•׳¨ ׳‘׳‘׳™׳¨׳•׳¨: '׳”׳×׳ ׳’׳“׳•׳× ׳׳×׳§׳‘׳׳×' ׳׳• '׳”׳×׳ ׳’׳“׳•׳× ׳ ׳“׳—׳™׳×' ׳¢׳ ׳”׳ ׳׳§׳” ׳§׳¦׳¨׳”."
        )

        messages = self._get_context_messages()

        if stream:
            full_response = "".join(
                chat_stream(messages=messages, system=system_with_ruling)
            )
        else:
            full_response = chat(messages=messages, system=system_with_ruling)
        self.conversation_history.append({"role": "judge", "content": full_response})
        self.orchestrator.add_conversation_message("judge", full_response)
        self.orchestrator.record_ruling()
        return full_response

    def ask_question(
        self,
        question_prompt: str = "",
        stream: bool = False,
    ) -> Union[str, Iterator[str]]:
        """
        Judge asks a probing question to the lawyer.

        Args:
            question_prompt: Optional context for what kind of question to ask
            stream: Whether to stream response

        Returns:
            Judge's question
        """
        system_with_question = (
            self._build_system_prompt()
            + f"\n\n׳¢׳›׳©׳™׳• ׳׳×׳” ׳©׳•׳׳ ׳©׳׳׳” ׳—׳“׳” ׳׳¢׳•׳¨׳ ׳”׳“׳™׳. {question_prompt or ''}"
        )

        messages = self._get_context_messages()

        if stream:
            full_response = "".join(
                chat_stream(messages=messages, system=system_with_question)
            )
        else:
            full_response = chat(messages=messages, system=system_with_question)
        self.conversation_history.append({"role": "judge", "content": full_response})
        self.orchestrator.add_conversation_message("judge", full_response)
        return full_response

    def advance_phase(self) -> str:
        """
        Judge advances to the next phase of the hearing.

        Returns:
            Announcement of the phase transition
        """
        new_phase = self.orchestrator.advance_phase()
        phase_name = self.orchestrator.get_phase_name_he()

        system_with_phase = (
            self._build_system_prompt() + f"\n\nהשלב הנוכחי עכשיו הוא: {phase_name}. "
            "פתח את השלב הזה באופן רשמי — הכרז על המעבר לשלב, "
            "תן הוראות קצרות לצדדים, ופתח את הדיון בשלב החדש. "
            "2-4 משפטים בעברית."
        )

        full_response = chat(messages=[], system=system_with_phase)
        self.conversation_history.append({"role": "judge", "content": full_response})
        self.orchestrator.add_conversation_message("judge", full_response)
        return full_response

    def get_conversation_history(self) -> List[Dict]:
        """Get the full conversation history with the judge."""
        return self.conversation_history

    def get_state_for_transcript(self) -> List[Dict]:
        """Get judge messages in orchestrator format for transcript."""
        return [
            msg
            for msg in self.orchestrator.get_state().conversation_history
            if msg.get("role") in ("judge", "lawyer", "attorney")
        ]
