import numpy as np

from engine import Grid

# Gosper Glider Gun needs at least this many rows/cols to avoid the gun
# wrapping into (and colliding with) itself on a toroidal grid.
GLIDER_GUN_MIN_SIZE = 40


def blinker(grid_size: int):
    return _centered([(0, 0), (0, 1), (0, 2)], grid_size)


def glider(grid_size: int):
    return _centered([(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)], grid_size)


def pulsar(grid_size: int):
    bar_rows = (0, 5, 7, 12)
    bar_cols = (2, 3, 4, 8, 9, 10)
    dot_rows = (2, 3, 4, 8, 9, 10)
    dot_cols = (0, 5, 7, 12)

    cells = [(r, c) for r in bar_rows for c in bar_cols]
    cells += [(r, c) for r in dot_rows for c in dot_cols]
    return _centered(cells, grid_size)


def glider_gun(grid_size: int):
    cells = [
        (0, 24),
        (1, 22), (1, 24),
        (2, 12), (2, 13), (2, 20), (2, 21), (2, 34), (2, 35),
        (3, 11), (3, 15), (3, 20), (3, 21), (3, 34), (3, 35),
        (4, 0), (4, 1), (4, 10), (4, 16), (4, 20), (4, 21),
        (5, 0), (5, 1), (5, 10), (5, 14), (5, 16), (5, 17), (5, 22), (5, 24),
        (6, 10), (6, 16), (6, 24),
        (7, 11), (7, 15),
        (8, 12), (8, 13),
    ]
    return _centered(cells, grid_size)


def _centered(cells, grid_size):
    max_row = max(r for r, _ in cells)
    max_col = max(c for _, c in cells)
    row_offset = (grid_size - max_row - 1) // 2
    col_offset = (grid_size - max_col - 1) // 2
    return [
        ((r + row_offset) % grid_size, (c + col_offset) % grid_size)
        for r, c in cells
    ]


_PATTERNS = {
    "blinker": blinker,
    "glider": glider,
    "pulsar": pulsar,
    "glider_gun": glider_gun,
}


def get_pattern(name: str, grid_size: int, seed: int | None = None) -> Grid:
    """Return a fully initialized Grid with the named pattern centered on it.

    `name` is case/space-insensitive (e.g. "Glider Gun", "glider_gun").
    "random" fills the grid with an independent random cell density instead
    of placing a fixed pattern.
    """
    key = name.strip().lower().replace(" ", "_")

    if key == "random":
        rng = np.random.default_rng(seed)
        cells = (rng.random((grid_size, grid_size)) < 0.3).astype(np.uint8)
        return Grid.from_array(cells)

    if key not in _PATTERNS:
        raise ValueError(f"Unknown pattern: {name!r}")

    grid = Grid(grid_size, grid_size)
    for r, c in _PATTERNS[key](grid_size):
        grid.set_cell(r, c, True)
    return grid
