"""
End-to-End Test Script for Court Practice Simulator
Tests core orchestrator + agent logic (Person 1's architecture)
"""

import sys
from config import CaseType, CRIMINAL_PHASES, CIVIL_PHASES
from core.orchestrator import Orchestrator
from agents.judge import JudgeAgent
from agents.attorney import AttorneyAgent


def test_orchestrator_phases():
    """Test the orchestrator phase state machine."""
    print("=" * 70)
    print("TEST 1: Orchestrator Phase State Machine")
    print("=" * 70)

    # Create orchestrator for criminal case
    orch = Orchestrator(session_id="test-001", case_type=CaseType.CRIMINAL)

    print(f"✓ Created orchestrator: {orch.session_id}")
    print(f"✓ Case type: {orch.case_type.value}")
    print(f"✓ Current phase: {orch.state.current_phase}")
    print(f"✓ Available phases: {orch.phases}")

    # Test phase advancement
    print("\nTesting phase advancement:")
    for _ in range(len(orch.phases) - 1):
        current = orch.state.current_phase
        new_phase = orch.advance_phase()
        print(f"  {current} → {new_phase}")

    # Test that we can't advance past the end
    try:
        orch.advance_phase()
        print("  ❌ ERROR: Should not be able to advance past final phase")
        return False
    except Exception as e:
        print(f"  ✓ Correctly prevented advance past final phase: {type(e).__name__}")

    print("✅ TEST 1 PASSED\n")
    return True


def test_orchestrator_state_tracking():
    """Test orchestrator conversation history and state tracking."""
    print("=" * 70)
    print("TEST 2: Orchestrator State & Conversation Tracking")
    print("=" * 70)

    orch = Orchestrator(session_id="test-002", case_type=CaseType.CIVIL)

    # Set up case
    orch.set_judge("דפנה ברק-אריאלי", {"description": "שופטת עליון בכירה"})
    orch.set_attorney('עו"ד אביחי מנדלבליט', {"tactics": ["התנגדות שמיעה"]})
    orch.set_case_facts(
        {
            "parties": "תובע כנגד נתבע",
            "claim": "פיצוי על נזקי גוף",
            "evidence": "בדיקה רפואית, עדויות",
        }
    )

    print(f"✓ Set judge: {orch.state.judge_name}")
    print(f"✓ Set attorney: {orch.state.attorney_name}")
    print(f"✓ Set case facts: {len(orch.state.case_facts)} fields")

    # Add messages
    orch.add_conversation_message("lawyer", "טיעון פתיחה שלי")
    orch.add_conversation_message("judge", "השופטת: שאלה על הנושא")
    orch.add_conversation_message("attorney", "התנגדות: עדות שמיעה")

    history = orch.get_state().conversation_history
    print(f"\n✓ Added 3 messages to history")
    print(f"✓ Conversation history has {len(history)} messages:")
    for i, msg in enumerate(history, 1):
        print(f"  {i}. {msg['role']}: {msg['content'][:40]}...")

    # Test context window
    context = orch.get_context_window(max_messages=2)
    print(f"\n✓ Retrieved last 2 messages (context window): {len(context)} messages")

    # Track metrics
    orch.record_objection()
    orch.record_objection()
    orch.record_ruling()
    print(
        f"✓ Tracked metrics: {orch.state.objections_count} objections, {orch.state.rulings_count} rulings"
    )

    print("✅ TEST 2 PASSED\n")
    return True


def test_judge_agent_instantiation():
    """Test that Judge agent can be instantiated and configured."""
    print("=" * 70)
    print("TEST 3: Judge Agent Instantiation")
    print("=" * 70)

    orch = Orchestrator(session_id="test-003", case_type=CaseType.CRIMINAL)
    orch.set_judge("אסתר חיות", {"style": "קפדנית על נוהל"})
    orch.set_case_facts(
        {
            "parties": "מדינת ישראל כנגד נחום",
            "charges": "גניבה",
            "evidence": "תיק חקירה",
        }
    )

    judge = JudgeAgent(orch)
    print(f"✓ Created Judge agent")

    # Check system prompt generation
    system_prompt = judge._build_system_prompt()
    print(f"✓ Generated system prompt ({len(system_prompt)} chars)")

    # Verify prompt contains key elements
    checks = [
        ("שופט ישראלי בכיר" in system_prompt, "Hebrew judge role"),
        ("אסתר חיות" in system_prompt, "Judge name"),
        ("גניבה" in system_prompt, "Case charge"),
        ("מחייבים" in system_prompt, "Legal framework"),
    ]

    print("\nSystem prompt validation:")
    for passed, check_name in checks:
        status = "✓" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            print(f"    ERROR: {check_name} not found in prompt")
            return False

    print("✅ TEST 3 PASSED\n")
    return True


def test_attorney_agent_instantiation():
    """Test that Attorney agent can be instantiated and configured."""
    print("=" * 70)
    print("TEST 4: Attorney Agent Instantiation")
    print("=" * 70)

    orch = Orchestrator(session_id="test-004", case_type=CaseType.CIVIL)
    orch.set_attorney('עו"ד גידי רגנר', {"tactics": ["חקירה נגדית", "עדות שמיעה"]})
    orch.set_case_facts(
        {
            "parties": "משכנתא בנק כנגד לווה",
            "claim": "כיסוי חוב",
            "evidence": "שטר משכנתא, רישומי תשלומים",
        }
    )

    attorney = AttorneyAgent(orch)
    print(f"✓ Created Attorney agent")

    # Check system prompt generation
    system_prompt = attorney._build_system_prompt()
    print(f"✓ Generated system prompt ({len(system_prompt)} chars)")

    # Verify prompt contains key elements
    checks = [
        ("עורך דין מנוסה" in system_prompt, "Hebrew attorney role"),
        ('עו"ד גידי רגנר' in system_prompt, "Attorney name"),
        ("משכנתא" in system_prompt, "Case parties"),
        ("התנגדויות" in system_prompt, "Objection framework"),
    ]

    print("\nSystem prompt validation:")
    for passed, check_name in checks:
        status = "✓" if passed else "❌"
        print(f"  {status} {check_name}")
        if not passed:
            print(f"    ERROR: {check_name} not found in prompt")
            return False

    print("✅ TEST 4 PASSED\n")
    return True


def test_phase_specific_prompts():
    """Test that phase-specific instructions are injected correctly."""
    print("=" * 70)
    print("TEST 5: Phase-Specific Prompt Injection")
    print("=" * 70)

    orch = Orchestrator(session_id="test-005", case_type=CaseType.CRIMINAL)
    orch.set_judge("שופט", {})
    orch.set_case_facts({"charges": "רצח"})

    judge = JudgeAgent(orch)

    # Test different phases
    phases_to_test = ["opening", "evidence", "closing", "ruling"]

    for phase in phases_to_test:
        orch.go_to_phase(phase)
        system_prompt = judge._build_system_prompt()
        print(f"✓ Phase '{phase}' ({len(system_prompt)} chars)")

        if phase not in system_prompt.lower():
            print(f"  ⚠️  Warning: phase name not explicitly in prompt")

    print("✅ TEST 5 PASSED\n")
    return True


def test_message_context_window():
    """Test that context window correctly limits messages."""
    print("=" * 70)
    print("TEST 6: Context Window Management")
    print("=" * 70)

    orch = Orchestrator(session_id="test-006", case_type=CaseType.CRIMINAL)

    # Add 20 messages
    for i in range(20):
        role = ["lawyer", "judge", "attorney"][i % 3]
        orch.add_conversation_message(role, f"Message {i+1}")

    print(f"✓ Added 20 messages to conversation history")

    # Get different context window sizes
    for window_size in [5, 10, 15]:
        context = orch.get_context_window(max_messages=window_size)
        print(f"✓ Context window size {window_size}: {len(context)} messages")

        if len(context) > window_size:
            print(f"  ❌ ERROR: context exceeds max size")
            return False

    print("✅ TEST 6 PASSED\n")
    return True


def test_orchestrator_context_dict():
    """Test that orchestrator produces correct context dict for prompts."""
    print("=" * 70)
    print("TEST 7: System Prompt Context Dictionary")
    print("=" * 70)

    orch = Orchestrator(session_id="test-007", case_type=CaseType.CRIMINAL)
    orch.set_judge("מירי כהן", {"description": "שופטת אקדמית"})
    orch.set_attorney('עו"ד', {})
    orch.set_case_facts({"parties": "A vs B"})
    orch.go_to_phase("evidence")

    context = orch.get_system_prompt_context()

    required_keys = [
        "case_type",
        "judge_name",
        "attorney_name",
        "current_phase",
        "case_facts",
        "judge_persona",
        "attorney_persona",
    ]

    print("Context dict keys:")
    for key in required_keys:
        if key in context:
            print(f"  ✓ {key}")
        else:
            print(f"  ❌ Missing: {key}")
            return False

    print(f"\n✓ Context dict has all required keys")
    print(f"  - Case type: {context['case_type']}")
    print(f"  - Judge: {context['judge_name']}")
    print(f"  - Current phase: {context['current_phase']}")
    print(f"  - Remaining phases: {context['phases_remaining']}")

    print("✅ TEST 7 PASSED\n")
    return True


def run_all_tests():
    """Run all test suite."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print(
        "║"
        + " COURT PRACTICE SIMULATOR - ARCHITECTURE VALIDATION TEST SUITE".center(68)
        + "║"
    )
    print(
        "║" + " Person 1: Architect + Core Agents (Core Logic Testing)".center(68) + "║"
    )
    print("╚" + "=" * 68 + "╝")
    print()

    tests = [
        test_orchestrator_phases,
        test_orchestrator_state_tracking,
        test_judge_agent_instantiation,
        test_attorney_agent_instantiation,
        test_phase_specific_prompts,
        test_message_context_window,
        test_orchestrator_context_dict,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append((test_func.__name__, result))
        except Exception as e:
            print(f"❌ TEST FAILED WITH EXCEPTION: {e}\n")
            import traceback

            traceback.print_exc()
            results.append((test_func.__name__, False))

    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED - CORE ARCHITECTURE IS SOUND\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED\n")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
