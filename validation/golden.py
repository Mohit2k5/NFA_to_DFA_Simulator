from typing import Optional
from engine.models import DFA
from engine.examples import EXAMPLES


def get_golden_dfa(example_id: str) -> Optional[DFA]:
    """Retrieves the pre-verified golden DFA for a built-in example."""
    if example_id in EXAMPLES:
        return EXAMPLES[example_id].golden_dfa
    return None
