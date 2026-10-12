"""Prop sizes in metres, shared by scripts/build_props.py and the cfgs.

Sized for the SO-101: about 0.45 m reach, jaws that close on ~2 cm.
Change a value here, then rebuild with `uv run python scripts/build_props.py`.
"""

TABLE_SIZE = (0.80, 0.70)  # x, y
TABLE_HEIGHT = 0.40
TABLE_TOP = 0.03
TABLE_LEG = 0.04

PAN_RADIUS = 0.06
PAN_WALL_HEIGHT = 0.03
PAN_THICKNESS = 0.004
PAN_HANDLE = (0.10, 0.018, 0.012)  # length, width, height
PAN_MASS = 0.15
PAN_WALL_SEGMENTS = 24

CABINET = (0.20, 0.22, 0.12)  # depth x, width y, height z
CABINET_WALL = 0.008
CABINET_MASS = 1.0
DRAWER_WALL = 0.006
DRAWER_CLEARANCE = 0.003
DRAWER_TRAVEL = 0.12
DRAWER_HANDLE = (0.02, 0.08, 0.015)
DRAWER_MASS = 0.15
