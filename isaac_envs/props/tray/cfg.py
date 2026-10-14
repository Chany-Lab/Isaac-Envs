"""16 x 12 cm tray with 3 cm walls, origin at its bottom, centred. Hand-written
USDA from Interface's sim assets."""

from __future__ import annotations

import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg

from isaac_envs import ASSETS_ROOT

TRAY_USD = ASSETS_ROOT / "props" / "tray" / "tray.usda"

TRAY_CFG = AssetBaseCfg(spawn=sim_utils.UsdFileCfg(usd_path=str(TRAY_USD)))
"""Static place target; it has no rigid body."""
