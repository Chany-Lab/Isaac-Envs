"""Ballpoint pen sizes in metres, shared by scripts/build_props.py and the cfg.

The barrel is a hexagon, so the pen lies on a flat and does not roll; the
SO-101 jaws close on it across the flats.
Change a value here, then rebuild with `uv run python scripts/build_props.py`.
"""

PEN_LENGTH = 0.14  # tip to back end
PEN_WIDTH = 0.010  # barrel, across the flats
PEN_TIP = (0.012, 0.002)  # length, radius
PEN_CAP_LENGTH = 0.045
PEN_CAP_WIDTH = 0.012  # across the flats
PEN_CLIP = (0.035, 0.003, 0.002)  # length, width, height
# Mass per part, kg; the body's mass and centre of mass are their sum.
PEN_BARREL_MASS = 0.005
PEN_CAP_MASS = 0.004
PEN_CLIP_MASS = 0.001
PEN_TIP_MASS = 0.002  # metal tip and ink
PEN_MASS = PEN_BARREL_MASS + PEN_CAP_MASS + PEN_CLIP_MASS + PEN_TIP_MASS  # 0.012
