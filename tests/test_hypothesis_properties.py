from hypothesis import given, settings, strategies as st
from engine.models import NFA
from engine.simulate import simulate_dfa, simulate_nfa
from engine.subset import subset_construction


@settings(max_examples=30, deadline=None)
@given(
    alphabet=st.just(["0", "1"]),
    num_states=st.integers(min_value=2, max_value=4),
    test_str=st.text(alphabet=["0", "1"], max_size=8),
)
def test_hypothesis_nfa_dfa_verdict_match(alphabet, num_states, test_str):
    states = [f"q{i}" for i in range(num_states)]
    start = states[0]
    # Simple transition generation:
    transitions = {}
    for s in states:
        transitions[s] = {
            "0": [states[(int(s[1:]) + 1) % num_states]],
            "1": [states[0], s],
        }

    accepts = [states[-1]]
    nfa = NFA(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        start=start,
        accepts=accepts,
    )

    dfa, _ = subset_construction(nfa)
    nfa_acc, _, _ = simulate_nfa(nfa, test_str)
    dfa_acc, _, _ = simulate_dfa(dfa, test_str)

    assert nfa_acc == dfa_acc, f"Hypothesis mismatch on string '{test_str}'"
