"""Ballpoint pen: one rigid body lying on a flat of its hexagonal barrel,
tip along +x, origin under the middle of the pen."""

from __future__ import annotations

import isaaclab.sim as sim_utils
from isaaclab.assets import RigidObjectCfg
from isaaclab_physx.sim.schemas import PhysxRigidBodyCfg

from isaac_envs import ASSETS_ROOT

PEN_USD = ASSETS_ROOT / "props" / "pen" / "pen.usd"

PEN_CFG = RigidObjectCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=str(PEN_USD),
        # Light and thin: more solver iterations keep it from jittering.
        rigid_props=PhysxRigidBodyCfg(
            solver_position_iteration_count=16,
            max_depenetration_velocity=1.0,
        ),
    ),
)
"""Pen the SO-101 can pick up across its barrel (12 g)."""
