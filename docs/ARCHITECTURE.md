# Architecture

## Toroidal boundary via modulo arithmetic

The grid has no edges: the cell at the last row/column is adjacent to the
cell at the first row/column, and vice versa. Rather than special-casing
edge and corner cells, every neighbor lookup wraps the row and column index
with the modulo operator: `(r + dr) % rows` and `(c + dc) % cols`. Because
Python's `%` always returns a non-negative result for a positive modulus
(even when `r + dr` is `-1`), this single expression handles all four edges
and all four corners uniformly, with no branching. See
`Grid.neighbor_count_naive` in `engine/grid.py`.

## Naive vs. vectorized neighbor counting

`neighbor_count_naive` walks every cell with a Python `for` loop and sums its
8 neighbors one at a time — `O(rows * cols * 8)` Python-level operations.
`neighbor_count_vectorized` instead convolves the whole grid against a 3x3
kernel of 1s (with a 0 in the center) using `scipy.signal.convolve2d(...,
boundary="wrap")`, which produces the same neighbor counts in a single call.

The vectorized version is faster because the O(rows * cols * 8) work still
happens, but inside SciPy's compiled C/Fortran routines operating on
contiguous NumPy memory, instead of as interpreted Python bytecode with
per-cell loop overhead, index arithmetic, and modulo calls. The naive method
is kept alongside it specifically so the two can be benchmarked and checked
against each other (see `test_neighbor_count_naive_vs_vectorized_agree`) —
it's the reference implementation the fast path is verified against, not a
fallback.

## Rules as birth/survive sets

Rule sets are plain dicts — `{"born": {...}, "survive": {...}}` — instead of
separate hardcoded functions or `if/elif` branches per rule type. A rule is
fully described by two sets of neighbor counts, so `CellularAutomaton.step()`
can implement every rule (Game of Life, HighLife, Seeds, and any future rule)
with the same two lines:

```python
born_mask = np.isin(counts, list(rule_set["born"])) & ~alive
survive_mask = np.isin(counts, list(rule_set["survive"])) & alive
```

Adding a new rule set is then just adding a new dict to `rules.py` — no
changes to the automaton logic, and no risk of the rule types drifting out
of sync with the stepping code.

## Glider gun toroidal collision

The Gosper Glider Gun's bounding box is 9 rows x 36 columns. On a grid
smaller than that, the modulo wraparound in the neighbor-counting logic
folds the gun's far edge back onto its own near edge, and `get_pattern`
itself will place gun cells at overlapping wrapped coordinates — collapsing
what should be 36 distinct live cells into fewer (e.g. 33 on a 20x20 grid,
see `test_glider_gun_avoids_self_collision`). The result isn't a clean
"gun that doesn't fit" — it's a corrupted gun that fires incorrectly or
dies out, because part of the pattern is silently overwriting another part.

`app.py` guards against this by defining `GLIDER_GUN_MIN_SIZE = 40` in
`patterns/presets.py` and, whenever the Glider Gun preset is selected with a
smaller grid size, clamping the effective grid size up to that minimum (and
showing a sidebar warning) before the grid is constructed — so the gun is
never placed somewhere it can collide with itself.
