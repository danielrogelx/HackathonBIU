"""
Coach Agent (Stub)
Person 4 (Data Engineering Student 2) will implement this

This agent analyzes the full session transcript and delivers a structured
debrief report with scores, strengths, weaknesses, procedural errors, and recommendations.
"""

from typing import Optional
from core.orchestrator import Orchestrator
from core.openrouter import chat
from core.prompts import get_coach_system_prompt


class CoachAgent:
    """
    Analyzes session transcripts and delivers debrief reports.

    TODO (Person 4):
    - Collect full session transcript from orchestrator
    - Call Claude with coach system prompt
    - Extract structured data: scores (5 dimensions), feedback, recommendations
    - Format as nice report for Streamlit display
    """

    def __init__(self, orchestrator: Orchestrator):
        """
        Initialize coach agent.

        Args:
            orchestrator: The session orchestrator with full transcript
        """
        self.orchestrator = orchestrator

    def generate_debrief(self) -> dict:
        """
        Generate a comprehensive debrief report for the session.

        Returns:
            Dict with:
            - overall_score: 1-10
            - dimensions: {
                "persuasion": 1-10,
                "legal_mastery": 1-10,
                "evidence_management": 1-10,
                "challenge_response": 1-10,
                "procedure": 1-10
              }
            - strengths: [list of strengths]
            - weaknesses: [list of weaknesses]
            - procedural_errors: [list of errors]
            - what_experts_do: str (how professionals would handle)
            - recommendations: [list of actionable recommendations]
            - full_analysis: str (raw analysis text)
        """
        # TODO: Person 4 to implement

        state = self.orchestrator.get_state()
        transcript = state.conversation_history

        # Call coach agent
        system_prompt = get_coach_system_prompt(
            case_type=state.case_type,
            transcript=transcript,
        )

        # Get analysis
        # analysis_text = chat(messages=[], system=system_prompt)

        # Parse and structure the response
        return {
            "overall_score": 0,
            "dimensions": {
                "persuasion": 0,
                "legal_mastery": 0,
                "evidence_management": 0,
                "challenge_response": 0,
                "procedure": 0,
            },
            "strengths": [],
            "weaknesses": [],
            "procedural_errors": [],
            "what_experts_do": "",
            "recommendations": [],
            "full_analysis": "",
        }
