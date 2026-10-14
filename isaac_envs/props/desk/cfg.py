"""Desk with a 1.2 x 0.8 m top, surface at 0.75 m, origin on the floor under the
middle. Hand-written USDA from Interface's sim assets (its `table`)."""

from __future__ import annotations

import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg

from isaac_envs import ASSETS_ROOT

DESK_USD = ASSETS_ROOT / "props" / "desk" / "desk.usda"

DESK_CFG = AssetBaseCfg(spawn=sim_utils.UsdFileCfg(usd_path=str(DESK_USD)))
"""Static desk; it never moves, so it has no rigid body."""
