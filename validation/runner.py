from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from engine.equivalence import check_equivalence_exhaustive
from engine.isomorphism import check_dfa_isomorphism
from engine.models import DFA, DFAState, NFA
from engine.simulate import simulate_dfa, simulate_nfa
from validation.golden import get_golden_dfa
from validation.test_cases import TestCase


@dataclass
class TestCaseResult:
    input_string: str
    expected: bool
    nfa_verdict: bool
    dfa_verdict: bool
    passed: bool
    description: str
    error: Optional[str] = None


@dataclass
class LayerAResult:
    results: List[TestCaseResult]
    total: int
    passed_count: int

    @property
    def all_passed(self) -> bool:
        return self.total > 0 and self.passed_count == self.total


@dataclass
class LayerBResult:
    is_equivalent: bool
    total_tested: int
    counterexample: Optional[str] = None
    nfa_verdict: Optional[bool] = None
    dfa_verdict: Optional[bool] = None


@dataclass
class LayerCResult:
    checked: bool
    matched: bool
    mapping: Dict[DFAState, Any]
    differences: List[str]
    note: str = ""


@dataclass
class ValidationReport:
    layer_a: LayerAResult
    layer_b: LayerBResult
    layer_c: LayerCResult

    @property
    def is_fully_valid(self) -> bool:
        layer_a_ok = self.layer_a.all_passed or self.layer_a.total == 0
        layer_b_ok = self.layer_b.is_equivalent
        layer_c_ok = (not self.layer_c.checked) or self.layer_c.matched
        return layer_a_ok and layer_b_ok and layer_c_ok


def run_validation(
    nfa: NFA,
    dfa: DFA,
    test_cases: Optional[List[TestCase]] = None,
    example_id: Optional[str] = None,
    golden_dfa: Optional[DFA] = None,
    exhaustive_max_length: int = 6,
) -> ValidationReport:
    """
    Runs the complete 3-layer validation pipeline:
    Layer A: Explicit Test Cases (Expected vs NFA vs DFA)
    Layer B: Automatic Equivalence Check (Exhaustive up to max_length)
    Layer C: Golden-DFA Comparison (Isomorphism check against stored reference)
    """
    # -------------------------------------------------------------
    # Layer A: Test cases
    # -------------------------------------------------------------
    tc_results: List[TestCaseResult] = []
    cases = test_cases or []
    passed_count = 0

    for tc in cases:
        nfa_acc, _, nfa_err = simulate_nfa(nfa, tc.input_string)
        dfa_acc, _, dfa_err = simulate_dfa(dfa, tc.input_string)
        err = nfa_err or dfa_err

        # Pass condition from section 8.2: expected == nfa_result == dfa_result
        passed = (tc.expected == nfa_acc == dfa_acc) and (err is None)
        if passed:
            passed_count += 1

        tc_results.append(
            TestCaseResult(
                input_string=tc.input_string,
                expected=tc.expected,
                nfa_verdict=nfa_acc,
                dfa_verdict=dfa_acc,
                passed=passed,
                description=tc.description,
                error=err,
            )
        )

    layer_a = LayerAResult(
        results=tc_results,
        total=len(cases),
        passed_count=passed_count,
    )

    # -------------------------------------------------------------
    # Layer B: Exhaustive Equivalence Check
    # -------------------------------------------------------------
    is_equiv, counter_str, nfa_v, dfa_v, total_t = check_equivalence_exhaustive(
        nfa, dfa, max_length=exhaustive_max_length
    )

    layer_b = LayerBResult(
        is_equivalent=is_equiv,
        total_tested=total_t,
        counterexample=counter_str,
        nfa_verdict=nfa_v,
        dfa_verdict=dfa_v,
    )

    # -------------------------------------------------------------
    # Layer C: Golden DFA Comparison
    # -------------------------------------------------------------
    ref_golden = golden_dfa
    if ref_golden is None and example_id:
        ref_golden = get_golden_dfa(example_id)

    if ref_golden is not None:
        is_iso, mapping, diffs = check_dfa_isomorphism(dfa, ref_golden)
        layer_c = LayerCResult(
            checked=True,
            matched=is_iso,
            mapping=mapping,
            differences=diffs,
            note="Compared with stored reference golden DFA via state graph isomorphism.",
        )
    else:
        layer_c = LayerCResult(
            checked=False,
            matched=False,
            mapping={},
            differences=[],
            note="Skipped (Golden DFA is only stored for built-in textbook examples; custom NFAs are validated via Layers A & B).",
        )

    return ValidationReport(layer_a=layer_a, layer_b=layer_b, layer_c=layer_c)
