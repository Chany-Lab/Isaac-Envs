"""4 cm cube, 50 g, origin at its bottom face, centred. Hand-written USDA from
Interface's sim assets."""

from __future__ import annotations

import isaaclab.sim as sim_utils
from isaaclab.assets import RigidObjectCfg

from isaac_envs import ASSETS_ROOT

CUBE_USD = ASSETS_ROOT / "props" / "cube" / "cube.usda"

CUBE_CFG = RigidObjectCfg(spawn=sim_utils.UsdFileCfg(usd_path=str(CUBE_USD)))
"""Cube to pick up (50 g)."""
