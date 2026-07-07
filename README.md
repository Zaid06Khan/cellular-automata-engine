# Cellular Automata Engine

A Python engine for simulating 2D cellular automata on a toroidal (wrap-around)
grid, with an interactive Streamlit UI for exploring classic rule sets and
patterns in real time. It's built to demonstrate core CS fundamentals — grid
algorithms, boundary handling, vectorized vs. naive computation, and
correctness testing against known-good patterns.

## What is a cellular automaton?

A cellular automaton is a grid of cells that are each either "alive" or
"dead," where every cell's next state is decided purely by a fixed rule
applied to how many of its neighbors are currently alive. The same simple
rule, applied to every cell simultaneously and repeated generation after
generation, is enough to produce surprisingly complex behavior — oscillators,
spaceships that travel across the grid, and self-sustaining structures.

## Rule sets implemented

Each rule set defines two conditions based on a cell's 8 neighbors:
- **Born**: a dead cell with this many live neighbors becomes alive.
- **Survive**: a live cell with this many live neighbors stays alive
  (otherwise it dies).

| Rule set | Born | Survive |
|---|---|---|
| Conway's Game of Life | {3} | {2, 3} |
| HighLife | {3, 6} | {2, 3} |
| Seeds | {2} | {} |

## Tech stack

- Python
- NumPy — grid storage and vectorized array operations
- SciPy — `scipy.signal.convolve2d` for fast neighbor counting
- Streamlit — interactive UI
- pytest — correctness tests

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Live demo

[Try the Cellular Automata Engine live](https://cellular-automata-engine-re7bnaxicljse67poxpjch.streamlit.app/)

Note: the app may take about 30-60 seconds to wake up if it's been inactive, since Streamlit Community Cloud puts idle apps to sleep.

## Testing

Run the test suite with:

```bash
pytest tests/
```

The 5 tests verify:
- **Naive/vectorized agreement** — the nested-loop neighbor count and the
  `convolve2d`-based neighbor count produce identical results on random
  grids.
- **Blinker period-2 oscillation** — a 3-cell blinker returns to its exact
  starting state after 2 generations (checked with both neighbor-counting
  methods).
- **Glider translation** — a glider shifts by exactly `(1, 1)` every 4
  generations, and by `(3, 3)` after 12 generations, with its live-cell
  count unchanged (shape preserved).
- **Pulsar period-3 oscillation** — the 48-cell pulsar preset returns to its
  starting state after 3 generations.
- **Glider gun self-collision guard** — the app enforces a minimum grid size
  for the Gosper Glider Gun so it doesn't wrap into and collide with itself
  on the toroidal grid.
