"""Small pan: one rigid body, origin at the centre of its base, handle along +x."""

from __future__ import annotations

import isaaclab.sim as sim_utils
from isaaclab.assets import RigidObjectCfg

from isaac_envs import ASSETS_ROOT

PAN_USD = ASSETS_ROOT / "props" / "pan" / "pan.usd"

PAN_CFG = RigidObjectCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=str(PAN_USD),
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            solver_position_iteration_count=8,
            max_depenetration_velocity=1.0,
        ),
    ),
)
"""Pan the SO-101 can lift by its handle (0.15 kg)."""
