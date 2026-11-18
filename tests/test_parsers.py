from engine.examples import EXAMPLES
from parsers.from_json import dfa_to_json, nfa_from_json, nfa_to_json
from parsers.from_table import nfa_to_table_rows, table_rows_to_nfa


def test_nfa_json_roundtrip():
    original_nfa = EXAMPLES["ends_with_01"].nfa
    json_str = nfa_to_json(original_nfa)
    restored_nfa = nfa_from_json(json_str)

    assert restored_nfa.states == original_nfa.states
    assert restored_nfa.alphabet == original_nfa.alphabet
    assert restored_nfa.start == original_nfa.start
    assert restored_nfa.accepts == original_nfa.accepts
    assert restored_nfa.transitions == original_nfa.transitions


def test_table_roundtrip():
    original_nfa = EXAMPLES["ends_with_01"].nfa
    rows = nfa_to_table_rows(original_nfa)
    restored_nfa, errors = table_rows_to_nfa(rows, original_nfa.alphabet)

    assert len(errors) == 0
    assert restored_nfa.states == original_nfa.states
    assert restored_nfa.start == original_nfa.start
    assert restored_nfa.accepts == original_nfa.accepts
