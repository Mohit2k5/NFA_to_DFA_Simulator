from dataclasses import dataclass
from typing import Dict, List
from engine.models import DFA, DFAState, NFA
from validation.test_cases import TestCase


@dataclass
class ExampleAutomaton:
    id: str
    name: str
    description: str
    nfa: NFA
    test_cases: List[TestCase]
    golden_dfa: DFA


def _build_examples() -> Dict[str, ExampleAutomaton]:
    examples: Dict[str, ExampleAutomaton] = {}

    # -------------------------------------------------------------
    # 1. Strings ending in "01"
    # -------------------------------------------------------------
    ex1_nfa = NFA(
        states=["q0", "q1", "q2"],
        alphabet=["0", "1"],
        transitions={
            "q0": {"0": ["q0", "q1"], "1": ["q0"]},
            "q1": {"1": ["q2"]},
            "q2": {},
        },
        start="q0",
        accepts=["q2"],
    )

    s_a: DFAState = frozenset(["q0"])
    s_b: DFAState = frozenset(["q0", "q1"])
    s_c: DFAState = frozenset(["q0", "q2"])

    ex1_golden = DFA(
        states=[s_a, s_b, s_c],
        alphabet=["0", "1"],
        transitions={
            s_a: {"0": s_b, "1": s_a},
            s_b: {"0": s_b, "1": s_c},
            s_c: {"0": s_b, "1": s_a},
        },
        start=s_a,
        accepts=[s_c],
    )

    ex1_tests = [
        TestCase("01", True, "Shortest matching string ending in 01"),
        TestCase("0101", True, "Multiple occurrences of 01"),
        TestCase("1101", True, "Prefix of 1s ending in 01"),
        TestCase("000001", True, "Prefix of 0s ending in 01"),
        TestCase("", False, "Empty string should be rejected"),
        TestCase("0", False, "Single 0 rejected"),
        TestCase("1", False, "Single 1 rejected"),
        TestCase("010", False, "Ends in 0 rejected"),
        TestCase("011", False, "Ends in 11 rejected"),
        TestCase("1111", False, "All 1s rejected"),
    ]

    examples["ends_with_01"] = ExampleAutomaton(
        id="ends_with_01",
        name="Strings ending in '01'",
        description="Classic textbook 3-state NFA recognizing binary strings that end in '01'.",
        nfa=ex1_nfa,
        test_cases=ex1_tests,
        golden_dfa=ex1_golden,
    )

    # -------------------------------------------------------------
    # 2. Strings containing substring "aba"
    # -------------------------------------------------------------
    ex2_nfa = NFA(
        states=["q0", "q1", "q2", "q3"],
        alphabet=["a", "b"],
        transitions={
            "q0": {"a": ["q0", "q1"], "b": ["q0"]},
            "q1": {"b": ["q2"]},
            "q2": {"a": ["q3"]},
            "q3": {"a": ["q3"], "b": ["q3"]},
        },
        start="q0",
        accepts=["q3"],
    )

    d_a: DFAState = frozenset(["q0"])
    d_b: DFAState = frozenset(["q0", "q1"])
    d_c: DFAState = frozenset(["q0", "q2"])
    d_d: DFAState = frozenset(["q0", "q1", "q3"])
    d_e: DFAState = frozenset(["q0", "q2", "q3"])
    d_f: DFAState = frozenset(["q0", "q3"])

    ex2_golden = DFA(
        states=[d_a, d_b, d_c, d_d, d_e, d_f],
        alphabet=["a", "b"],
        transitions={
            d_a: {"a": d_b, "b": d_a},
            d_b: {"a": d_b, "b": d_c},
            d_c: {"a": d_d, "b": d_a},
            d_d: {"a": d_d, "b": d_e},
            d_e: {"a": d_d, "b": d_f},
            d_f: {"a": d_d, "b": d_f},
        },
        start=d_a,
        accepts=[d_d, d_e, d_f],
    )

    ex2_tests = [
        TestCase("aba", True, "Exact match for substring 'aba'"),
        TestCase("aaba", True, "Leading 'a' then 'aba'"),
        TestCase("ababa", True, "Overlapping 'aba' substring"),
        TestCase("babab", True, "'aba' embedded inside 'b' characters"),
        TestCase("", False, "Empty string rejected"),
        TestCase("a", False, "Incomplete prefix 'a'"),
        TestCase("ab", False, "Incomplete prefix 'ab'"),
        TestCase("ba", False, "Non-matching 'ba'"),
        TestCase("abb", False, "Broken sequence 'abb'"),
        TestCase("bbba", False, "No 'aba' present"),
    ]

    examples["contains_aba"] = ExampleAutomaton(
        id="contains_aba",
        name="Strings containing 'aba'",
        description="NFA that nondeterministically branches on 'a' to search for substring 'aba'.",
        nfa=ex2_nfa,
        test_cases=ex2_tests,
        golden_dfa=ex2_golden,
    )

    # -------------------------------------------------------------
    # 3. Second symbol from end is 'a'
    # -------------------------------------------------------------
    ex3_nfa = NFA(
        states=["q0", "q1", "q2"],
        alphabet=["a", "b"],
        transitions={
            "q0": {"a": ["q0", "q1"], "b": ["q0"]},
            "q1": {"a": ["q2"], "b": ["q2"]},
            "q2": {},
        },
        start="q0",
        accepts=["q2"],
    )

    t0: DFAState = frozenset(["q0"])
    t1: DFAState = frozenset(["q0", "q1"])
    t2: DFAState = frozenset(["q0", "q1", "q2"])
    t3: DFAState = frozenset(["q0", "q2"])

    ex3_golden = DFA(
        states=[t0, t1, t2, t3],
        alphabet=["a", "b"],
        transitions={
            t0: {"a": t1, "b": t0},
            t1: {"a": t2, "b": t3},
            t2: {"a": t2, "b": t3},
            t3: {"a": t1, "b": t0},
        },
        start=t0,
        accepts=[t2, t3],
    )

    ex3_tests = [
        TestCase("aa", True, "Length 2: 2nd from end is 'a'"),
        TestCase("ab", True, "Length 2: 2nd from end is 'a'"),
        TestCase("baa", True, "Length 3: 2nd from end is 'a'"),
        TestCase("bab", True, "Length 3: 2nd from end is 'a'"),
        TestCase("bbaa", True, "Length 4: 2nd from end is 'a'"),
        TestCase("", False, "Empty string rejected"),
        TestCase("a", False, "Length 1 has no 2nd from end"),
        TestCase("b", False, "Length 1 has no 2nd from end"),
        TestCase("bb", False, "2nd from end is 'b'"),
        TestCase("aba", False, "2nd from end is 'b'"),
    ]

    examples["second_from_end_a"] = ExampleAutomaton(
        id="second_from_end_a",
        name="Second symbol from end is 'a'",
        description="Textbook example showing nondeterministic guessing of when the word is 2 symbols from ending.",
        nfa=ex3_nfa,
        test_cases=ex3_tests,
        golden_dfa=ex3_golden,
    )

    # -------------------------------------------------------------
    # 4. Starts with '0' and ends with '1' (Produces Trap State ∅)
    # -------------------------------------------------------------
    ex4_nfa = NFA(
        states=["q0", "q1", "q2"],
        alphabet=["0", "1"],
        transitions={
            "q0": {"0": ["q1"]},  # missing on '1' -> leads to ∅ !
            "q1": {"0": ["q1"], "1": ["q1", "q2"]},
            "q2": {"0": ["q1"], "1": ["q1", "q2"]},
        },
        start="q0",
        accepts=["q2"],
    )

    p0: DFAState = frozenset(["q0"])
    p1: DFAState = frozenset(["q1"])
    p2: DFAState = frozenset(["q1", "q2"])
    ptrap: DFAState = frozenset()

    ex4_golden = DFA(
        states=[p0, p1, p2, ptrap],
        alphabet=["0", "1"],
        transitions={
            p0: {"0": p1, "1": ptrap},
            p1: {"0": p1, "1": p2},
            p2: {"0": p1, "1": p2},
            ptrap: {"0": ptrap, "1": ptrap},
        },
        start=p0,
        accepts=[p2],
    )

    ex4_tests = [
        TestCase("01", True, "Starts with 0, ends with 1"),
        TestCase("001", True, "Starts with 0, middle 0, ends with 1"),
        TestCase("011", True, "Starts with 0, repeated 1s at end"),
        TestCase("000101", True, "Longer alternating sequence ending in 1"),
        TestCase("", False, "Empty string rejected"),
        TestCase("1", False, "Starts with 1 (hits trap state ∅)"),
        TestCase("10", False, "Starts with 1 (hits trap state ∅)"),
        TestCase("0", False, "Starts with 0 but does not end with 1"),
        TestCase("00", False, "Starts with 0 but ends with 0"),
        TestCase("010", False, "Starts with 0, has 1, but ends with 0"),
    ]

    examples["starts_0_ends_1"] = ExampleAutomaton(
        id="starts_0_ends_1",
        name="Starts with '0' and ends with '1' (Trap State ∅)",
        description="NFA with missing initial transition on '1', explicitly testing generation of the dead/trap state ∅.",
        nfa=ex4_nfa,
        test_cases=ex4_tests,
        golden_dfa=ex4_golden,
    )

    # -------------------------------------------------------------
    # 5. Strings containing both 'a' and 'b'
    # -------------------------------------------------------------
    ex5_nfa = NFA(
        states=["q0", "q1", "q2", "q3"],
        alphabet=["a", "b"],
        transitions={
            "q0": {"a": ["q1"], "b": ["q2"]},
            "q1": {"a": ["q1"], "b": ["q3"]},
            "q2": {"a": ["q3"], "b": ["q2"]},
            "q3": {"a": ["q3"], "b": ["q3"]},
        },
        start="q0",
        accepts=["q3"],
    )

    r0: DFAState = frozenset(["q0"])
    r1: DFAState = frozenset(["q1"])
    r2: DFAState = frozenset(["q2"])
    r3: DFAState = frozenset(["q3"])

    ex5_golden = DFA(
        states=[r0, r1, r2, r3],
        alphabet=["a", "b"],
        transitions={
            r0: {"a": r1, "b": r2},
            r1: {"a": r1, "b": r3},
            r2: {"a": r3, "b": r2},
            r3: {"a": r3, "b": r3},
        },
        start=r0,
        accepts=[r3],
    )

    ex5_tests = [
        TestCase("ab", True, "Shortest containing both 'a' and 'b'"),
        TestCase("ba", True, "Shortest containing 'b' then 'a'"),
        TestCase("aab", True, "Multiple 'a's then 'b'"),
        TestCase("bba", True, "Multiple 'b's then 'a'"),
        TestCase("abba", True, "Contains both"),
        TestCase("", False, "Empty string rejected"),
        TestCase("a", False, "Only 'a' rejected"),
        TestCase("b", False, "Only 'b' rejected"),
        TestCase("aaaa", False, "All 'a's rejected"),
        TestCase("bbbb", False, "All 'b's rejected"),
    ]

    examples["contains_both_a_and_b"] = ExampleAutomaton(
        id="contains_both_a_and_b",
        name="Contains both 'a' and 'b'",
        description="NFA that branches to check if both characters 'a' and 'b' appear in the string.",
        nfa=ex5_nfa,
        test_cases=ex5_tests,
        golden_dfa=ex5_golden,
    )

    # -------------------------------------------------------------
    # 6. Already Deterministic NFA (Divisible by 3 zeros)
    # -------------------------------------------------------------
    ex6_nfa = NFA(
        states=["q0", "q1", "q2"],
        alphabet=["0", "1"],
        transitions={
            "q0": {"0": ["q1"], "1": ["q0"]},
            "q1": {"0": ["q2"], "1": ["q1"]},
            "q2": {"0": ["q0"], "1": ["q2"]},
        },
        start="q0",
        accepts=["q0"],
    )

    m0: DFAState = frozenset(["q0"])
    m1: DFAState = frozenset(["q1"])
    m2: DFAState = frozenset(["q2"])

    ex6_golden = DFA(
        states=[m0, m1, m2],
        alphabet=["0", "1"],
        transitions={
            m0: {"0": m1, "1": m0},
            m1: {"0": m2, "1": m1},
            m2: {"0": m0, "1": m2},
        },
        start=m0,
        accepts=[m0],
    )

    ex6_tests = [
        TestCase("", True, "0 zeros is divisible by 3"),
        TestCase("1", True, "No zeros, 1s leave in accept state"),
        TestCase("000", True, "Exactly three 0s"),
        TestCase("1010101", True, "Three 0s interspersed with 1s"),
        TestCase("0", False, "One 0 rejected"),
        TestCase("00", False, "Two 0s rejected"),
        TestCase("0000", False, "Four 0s rejected"),
    ]

    examples["mod_3_zeros"] = ExampleAutomaton(
        id="mod_3_zeros",
        name="Count of '0's is divisible by 3 (Already Deterministic)",
        description="Edge case test: an already deterministic automaton where each DFA state is a singleton set.",
        nfa=ex6_nfa,
        test_cases=ex6_tests,
        golden_dfa=ex6_golden,
    )

    return examples


EXAMPLES = _build_examples()
