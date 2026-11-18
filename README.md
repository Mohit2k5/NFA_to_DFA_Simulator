# NFA → DFA Conversion Simulator

**Course:** CSET302 – Automata Theory and Computability  
**Topic:** NFA to DFA conversion using the **subset construction** algorithm  
**Scope:** Plain NFAs only (no ε-transitions).

---

## 🚀 Overview

An interactive, visual, and mathematically rigorous web simulator that converts any user-defined non-deterministic finite automaton (NFA) into an equivalent deterministic finite automaton (DFA) using the **subset construction** algorithm.

The simulator strictly follows the course's required pipeline:
```
User Input ➔ Algorithm ➔ Step-by-Step Walkthrough / Visualization ➔ Result Summary ➔ Multi-Layer Validation
```

---

## ✨ Features

- **Dynamic NFA Definition & Input:**
  - Interactive transition table editor (`st.data_editor`) with Start/Accept checkboxes and multi-target inputs.
  - JSON import and export.
  - 6 preloaded textbook examples covering classic languages, edge cases, trap states, and deterministic automata.
  - Robust validation: rejects ε-transitions (`ε`, `λ`, `e`, `epsilon`), invalid alphabet symbols, unreachable states, or malformed transitions with immediate error feedback.
- **Step-by-Step Walkthrough & Progressive Visualization:**
  - Replay controls: `⏮ First`, `◀ Prev`, `▶ Next`, `⏭ End`, `🔄 Reset`, and `▶️ Auto-play` with an adjustable speed slider.
  - Interactive step slider to jump directly to any state in the trace.
  - Colored explanation cards detailing the exact mathematical operation at each step (`move(T, a)`, discovering new states, linking existing states, marking accept states).
- **Side-by-Side Graphviz Visualizations:**
  - Clean Graphviz DOT rendering (`rankdir=LR`, start state arrow, double circles for accepting states, merged parallel edge labels).
  - Progressive graph updates that reveal DFA states and transitions as the algorithm discovers them.
  - Active state and edge highlighting during step playback.
  - Optional toggle to hide or show the trap/dead state (∅).
- **Interactive String Tester:**
  - Test any string over the alphabet (including the empty string ε).
  - Synchronous execution on both NFA (active subset) and DFA (active state).
  - Scrubber slider to step through the string character-by-character.
  - Agreement checker alerting immediately if NFA and DFA verdicts diverge.
- **Comprehensive 3-Layer Validation Suite:**
  - **Layer A (Test Cases):** Expected vs NFA vs DFA verdicts across test suites. Users can add custom test cases live.
  - **Layer B (Exhaustive Equivalence Check):** Exhaustively tests all strings over the alphabet up to length $N$ ($N \in [3, 8]$) to prove behavioral equivalence or pinpoint a counterexample.
  - **Layer C (Golden-DFA Isomorphism Check):** Verifies the generated DFA's graph structure against a known-correct textbook reference DFA using bijection and isomorphism checking.
- **DFA Minimization & Export:**
  - Hopcroft / Table-Filling partition refinement algorithm to compute the minimal DFA.
  - Before vs after state count comparison and minimized DFA graph rendering.
  - Export to JSON, Graphviz DOT, and LaTeX / TikZ automata code.

---

## 🏗️ Architecture & Folder Structure

```
d:\NFA_to_DFA_Sim\
  ├── app.py                      # Streamlit application entry point
  ├── requirements.txt            # Python dependencies
  ├── README.md                   # Project documentation
  ├── engine/                     # Pure Python core algorithm engine
  │   ├── models.py               # NFA, DFA, TraceStep dataclasses
  │   ├── validate.py             # NFA input validation & epsilon rejection
  │   ├── move.py                 # move(S, a) operation on state subsets
  │   ├── subset.py               # Subset construction algorithm & step trace
  │   ├── simulate.py             # String execution on NFA and DFA
  │   ├── equivalence.py          # Layer B: exhaustive equivalence checking
  │   ├── isomorphism.py          # Layer C: DFA graph isomorphism comparison
  │   ├── minimize.py             # DFA minimization (Hopcroft partition refinement)
  │   └── examples.py             # 6 built-in textbook example automata
  ├── validation/                 # Multi-layer validation module
  │   ├── test_cases.py           # TestCase dataclass & suites
  │   ├── golden.py               # Golden reference DFAs
  │   └── runner.py               # Validation execution & reporting
  ├── parsers/                    # Serialization & data interchange
  │   ├── from_json.py            # JSON serialization/deserialization
  │   └── from_table.py           # Streamlit table editor converter
  ├── ui/                         # Streamlit visual components
  │   ├── nfa_editor.py           # Sidebar input editor & example selector
  │   ├── graph_view.py           # Graphviz DOT generators with highlights
  │   ├── tables.py               # Transition table formatters
  │   ├── step_controls.py        # Playback navigation bar & speed controls
  │   ├── explanation.py          # Step explanation callout cards
  │   ├── string_tester.py        # String simulator & character scrubber
  │   ├── result_panel.py         # Metrics, minimization & exports
  │   └── validation_panel.py     # 3-Layer validation tabs
  └── tests/                      # Automated unit and property test suites
      ├── test_validate.py
      ├── test_move.py
      ├── test_subset.py
      ├── test_simulate.py
      ├── test_equivalence.py
      ├── test_isomorphism.py
      ├── test_minimize.py
      ├── test_parsers.py
      ├── test_validation.py
      └── test_hypothesis_properties.py
```

---

## 📦 Setup & Installation

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Virtual environment (`.venv`)

### 2. Activate Virtual Environment & Install Dependencies

```powershell
# In PowerShell:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Run the Streamlit Web Application

```powershell
.\.venv\Scripts\streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🧪 Running Automated Tests

Run the full test suite with `pytest`:

```powershell
.\.venv\Scripts\pytest -v
```

All 21 unit, integration, and Hypothesis property tests will execute in under 1 second.

---

## 📚 Built-in Textbook Examples

1. **Strings ending in `01`** (`ends_with_01`): Classic 3-state NFA converted into 3 DFA states.
2. **Strings containing substring `aba`** (`contains_aba`): Nondeterministic substring matching converted into a 6-state DFA.
3. **Second symbol from end is `'a'`** (`second_from_end_a`): Nondeterministic guess converted into a 4-state DFA.
4. **Starts with `'0'` and ends with `'1'`** (`starts_0_ends_1`): Tests generation and transitions into the dead/trap state $\emptyset$.
5. **Contains both `'a'` and `'b'`** (`contains_both_a_and_b`): Multi-branch NFA converted into a 4-state DFA.
6. **Count of `'0'`s divisible by 3** (`mod_3_zeros`): Deterministic NFA edge case testing singleton state sets.
