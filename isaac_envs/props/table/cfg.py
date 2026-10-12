"""Heavy-duty packing table (Isaac Sim's, as in Isaac Lab's humanoid tasks):
static colliders, origin on the floor under the middle, top at `TABLE_HEIGHT`,
depth along x and length along y."""

from __future__ import annotations

import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg

from isaac_envs import ASSETS_ROOT
from isaac_envs.props.table.dims import TABLE_HEIGHT, TABLE_SIZE

TABLE_USD = ASSETS_ROOT / "props" / "table" / "table.usda"

TABLE_CFG = AssetBaseCfg(spawn=sim_utils.UsdFileCfg(usd_path=str(TABLE_USD)))
"""Static table; it never moves, so it has no rigid body."""

__all__ = ["TABLE_CFG", "TABLE_HEIGHT", "TABLE_SIZE"]
