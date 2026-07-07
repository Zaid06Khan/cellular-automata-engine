import time

import numpy as np
import streamlit as st
from PIL import Image

from engine import GAME_OF_LIFE, HIGHLIFE, SEEDS, CellularAutomaton
from patterns import get_pattern, GLIDER_GUN_MIN_SIZE

RULESETS = {
    "Conway's Game of Life": GAME_OF_LIFE,
    "HighLife": HIGHLIFE,
    "Seeds": SEEDS,
}
PATTERNS = ["Random", "Blinker", "Glider", "Pulsar", "Glider Gun"]

st.set_page_config(page_title="Cellular Automata Engine", layout="wide")
st.title("Cellular Automata Engine")


def init_state(grid_size: int, pattern_name: str, rule_name: str) -> None:
    grid = get_pattern(pattern_name, grid_size)
    st.session_state.automaton = CellularAutomaton(grid, RULESETS[rule_name])
    st.session_state.generation = 0
    st.session_state.running = False


def render_grid(cells: np.ndarray) -> Image.Image:
    scale = max(4, 640 // cells.shape[0])
    pixels = np.where(cells.astype(bool), 255, 20).astype(np.uint8)
    img = Image.fromarray(pixels, mode="L")
    return img.resize((cells.shape[1] * scale, cells.shape[0] * scale), Image.NEAREST)


if "automaton" not in st.session_state:
    init_state(40, "Random", "Conway's Game of Life")
    st.session_state.config = (40, "Random", "Conway's Game of Life")

st.sidebar.header("Controls")
rule_name = st.sidebar.selectbox("Rule set", list(RULESETS.keys()))
pattern_name = st.sidebar.selectbox("Pattern", PATTERNS)
grid_size = st.sidebar.slider("Grid size", 20, 80, 40)
speed = st.sidebar.slider("Speed (generations/sec)", 1, 20, 5)

if pattern_name == "Glider Gun" and grid_size < GLIDER_GUN_MIN_SIZE:
    st.sidebar.warning(
        f"Glider Gun needs at least {GLIDER_GUN_MIN_SIZE}x{GLIDER_GUN_MIN_SIZE} "
        f"to avoid wrapping into itself. Using {GLIDER_GUN_MIN_SIZE}x{GLIDER_GUN_MIN_SIZE}."
    )
    grid_size = GLIDER_GUN_MIN_SIZE

config = (grid_size, pattern_name, rule_name)
if st.session_state.config != config:
    init_state(*config)
    st.session_state.config = config

col1, col2, col3 = st.sidebar.columns(3)
if col1.button("Pause" if st.session_state.running else "Play"):
    st.session_state.running = not st.session_state.running
if col2.button("Step"):
    st.session_state.automaton.step()
    st.session_state.generation += 1
if col3.button("Reset"):
    init_state(*config)

automaton = st.session_state.automaton
live_count = int(np.sum(automaton.grid.cells))

m1, m2 = st.columns(2)
m1.metric("Generation", st.session_state.generation)
m2.metric("Live cells", live_count)

placeholder = st.empty()
placeholder.image(render_grid(automaton.grid.cells))

if st.session_state.running:
    time.sleep(1.0 / speed)
    automaton.step()
    st.session_state.generation += 1
    st.rerun()
