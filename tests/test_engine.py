import numpy as np

from engine import Grid, GAME_OF_LIFE, CellularAutomaton
from patterns import get_pattern, GLIDER_GUN_MIN_SIZE


def make_grid(rows, cols, live_cells):
    arr = np.zeros((rows, cols), dtype=np.uint8)
    for r, c in live_cells:
        arr[r, c] = 1
    return Grid.from_array(arr)


def test_neighbor_count_naive_vs_vectorized_agree():
    rng = np.random.default_rng(42)
    arr = (rng.random((10, 10)) > 0.5).astype(np.uint8)
    grid = Grid.from_array(arr)
    naive = grid.neighbor_count_naive()
    vectorized = grid.neighbor_count_vectorized()
    assert np.array_equal(naive, vectorized)


def test_blinker_oscillates_with_period_2():
    # Horizontal blinker in the middle of a 10x10 grid.
    rows, cols = 10, 10
    live_cells = [(5, 4), (5, 5), (5, 6)]
    expected_gen1 = make_grid(rows, cols, [(4, 5), (5, 5), (6, 5)])

    for use_vectorized in (True, False):
        grid = make_grid(rows, cols, live_cells)
        ca = CellularAutomaton(grid, GAME_OF_LIFE, use_vectorized=use_vectorized)

        gen0 = ca.grid.copy()
        gen1 = ca.step().copy()
        gen2 = ca.step().copy()

        # After one step, blinker should have flipped to vertical (different from gen0).
        assert gen1 != gen0
        assert gen1 == expected_gen1
        # After two steps, it should match the original state (period 2).
        assert gen2 == gen0


def test_glider_translates_diagonally_every_4_generations():
    # Standard glider pattern, moves down-right by (1, 1) every 4 generations.
    rows, cols = 20, 20
    live_cells = [(1, 2), (2, 3), (3, 1), (3, 2), (3, 3)]
    grid = make_grid(rows, cols, live_cells)
    ca = CellularAutomaton(grid, GAME_OF_LIFE)

    gen0_cells = ca.grid.cells.copy()

    for _ in range(4):
        ca.step()
    gen4_cells = ca.grid.cells.copy()

    # The pattern should be identical to gen0 but shifted by (1, 1) (toroidal roll).
    assert np.array_equal(gen4_cells, np.roll(gen0_cells, shift=(1, 1), axis=(0, 1)))
    # Shape (number of live cells) is unchanged.
    assert np.sum(gen4_cells) == np.sum(gen0_cells) == 5

    for _ in range(8):
        ca.step()
    gen12_cells = ca.grid.cells

    # Still holds after multiple periods (3 * (1, 1) = (3, 3)).
    assert np.array_equal(gen12_cells, np.roll(gen0_cells, shift=(3, 3), axis=(0, 1)))


def test_pulsar_oscillates_with_period_3():
    grid = get_pattern("Pulsar", 40)
    ca = CellularAutomaton(grid, GAME_OF_LIFE)

    gen0 = ca.grid.copy()
    for _ in range(3):
        ca.step()

    assert ca.grid == gen0
    assert np.sum(gen0.cells) == 48


def test_glider_gun_avoids_self_collision():
    # At or above the minimum size, all 36 gun cells remain distinct.
    safe_grid = get_pattern("Glider Gun", GLIDER_GUN_MIN_SIZE)
    assert int(np.sum(safe_grid.cells)) == 36

    # Below the minimum, toroidal wraparound folds cells onto each other,
    # which is exactly what the app.py guard prevents.
    cramped_grid = get_pattern("Glider Gun", 20)
    assert int(np.sum(cramped_grid.cells)) < 36
