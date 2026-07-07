import numpy as np

from .grid import Grid


class CellularAutomaton:
    """Advances a Grid one generation at a time according to a rule set."""

    def __init__(self, grid: Grid, rule_set: dict, use_vectorized: bool = True):
        self.grid = grid
        self.rule_set = rule_set
        self.use_vectorized = use_vectorized

    def step(self) -> Grid:
        if self.use_vectorized:
            counts = self.grid.neighbor_count_vectorized()
        else:
            counts = self.grid.neighbor_count_naive()

        alive = self.grid.cells.astype(bool)
        born_mask = np.isin(counts, list(self.rule_set["born"])) & ~alive
        survive_mask = np.isin(counts, list(self.rule_set["survive"])) & alive

        new_cells = (born_mask | survive_mask).astype(np.uint8)
        self.grid = Grid(self.grid.rows, self.grid.cols, new_cells)
        return self.grid
