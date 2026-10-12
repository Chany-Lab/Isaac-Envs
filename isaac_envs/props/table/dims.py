"""Table sizes in metres, shared by scripts/build_props.py and the cfg.

A steel workbench at standard height, big enough that an arm can be mounted
on it or a humanoid can stand at its edge.
Change a value here, then rebuild with `uv run python scripts/build_props.py`.
"""

TABLE_SIZE = (1.20, 0.80)  # x, y
TABLE_HEIGHT = 0.75
TABLE_TOP = 0.04
TABLE_LEG = 0.05  # square tube
TABLE_APRON = (0.08, 0.03)  # height, thickness of the frame under the top
