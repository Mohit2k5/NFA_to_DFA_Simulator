from engine.examples import EXAMPLES
from engine.subset import subset_construction
from validation.runner import run_validation


def test_validation_runner_full_pass():
    ex = EXAMPLES["ends_with_01"]
    dfa, _ = subset_construction(ex.nfa)

    report = run_validation(
        nfa=ex.nfa,
        dfa=dfa,
        test_cases=ex.test_cases,
        example_id="ends_with_01",
        golden_dfa=ex.golden_dfa,
        exhaustive_max_length=5,
    )

    assert report.is_fully_valid is True
    assert report.layer_a.all_passed is True
    assert report.layer_a.passed_count == len(ex.test_cases)
    assert report.layer_b.is_equivalent is True
    assert report.layer_c.matched is True
