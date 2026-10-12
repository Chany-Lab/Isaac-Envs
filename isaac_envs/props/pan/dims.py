"""Pan sizes in metres, shared by scripts/build_props.py and the cfg.

Change a value here, then rebuild with `uv run python scripts/build_props.py`.
"""

PAN_RADIUS = 0.06
PAN_WALL_HEIGHT = 0.03
PAN_THICKNESS = 0.004
PAN_HANDLE = (0.10, 0.018, 0.012)  # length, width, height
# Mass per part, kg; the body's mass and centre of mass are their sum, so the
# handle pulls the centre of mass towards +x.
PAN_BOTTOM_MASS = 0.06
PAN_WALL_MASS = 0.06  # whole ring, spread over the segments
PAN_HANDLE_MASS = 0.03
PAN_MASS = PAN_BOTTOM_MASS + PAN_WALL_MASS + PAN_HANDLE_MASS  # 0.15
PAN_WALL_SEGMENTS = 24
