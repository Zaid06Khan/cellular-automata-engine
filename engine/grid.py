import numpy as np
from scipy.signal import convolve2d

_NEIGHBOR_OFFSETS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
]

_NEIGHBOR_KERNEL = np.array(
    [[1, 1, 1],
     [1, 0, 1],
     [1, 1, 1]],
    dtype=np.uint8,
)


class Grid:
    """A 2D toroidal (wrap-around) grid of cells backed by a NumPy uint8 array."""

    def __init__(self, rows: int, cols: int, cells: np.ndarray | None = None):
        self.rows = rows
        self.cols = cols
        if cells is None:
            self.cells = np.zeros((rows, cols), dtype=np.uint8)
        else:
            if cells.shape != (rows, cols):
                raise ValueError(
                    f"cells shape {cells.shape} does not match ({rows}, {cols})"
                )
            self.cells = cells.astype(np.uint8)

    @classmethod
    def from_array(cls, array) -> "Grid":
        arr = np.asarray(array, dtype=np.uint8)
        rows, cols = arr.shape
        return cls(rows, cols, arr)

    def copy(self) -> "Grid":
        return Grid(self.rows, self.cols, self.cells.copy())

    def set_cell(self, row: int, col: int, alive: bool) -> None:
        self.cells[row % self.rows, col % self.cols] = 1 if alive else 0

    def get_cell(self, row: int, col: int) -> int:
        return int(self.cells[row % self.rows, col % self.cols])

    def neighbor_count_naive(self) -> np.ndarray:
        """Naive nested-loop toroidal neighbor count using modulo arithmetic."""
        counts = np.zeros((self.rows, self.cols), dtype=np.uint8)
        for r in range(self.rows):
            for c in range(self.cols):
                total = 0
                for dr, dc in _NEIGHBOR_OFFSETS:
                    nr = (r + dr) % self.rows
                    nc = (c + dc) % self.cols
                    total += self.cells[nr, nc]
                counts[r, c] = total
        return counts

    def neighbor_count_vectorized(self) -> np.ndarray:
        """Vectorized toroidal neighbor count using scipy.signal.convolve2d."""
        result = convolve2d(
            self.cells, _NEIGHBOR_KERNEL, mode="same", boundary="wrap"
        )
        return result.astype(np.uint8)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Grid):
            return NotImplemented
        return (
            self.rows == other.rows
            and self.cols == other.cols
            and np.array_equal(self.cells, other.cells)
        )

    def __repr__(self) -> str:
        return f"Grid({self.rows}x{self.cols})"
