"""Cabinet and drawer sizes in metres, shared by scripts/build_props.py and
the cfg.

Change a value here, then rebuild with `uv run python scripts/build_props.py`.
"""

CABINET = (0.20, 0.22, 0.12)  # depth x, width y, height z
CABINET_WALL = 0.008
CABINET_MASS = 1.0
DRAWER_WALL = 0.006
DRAWER_CLEARANCE = 0.003
DRAWER_TRAVEL = 0.12
DRAWER_HANDLE = (0.02, 0.08, 0.015)
DRAWER_MASS = 0.15
