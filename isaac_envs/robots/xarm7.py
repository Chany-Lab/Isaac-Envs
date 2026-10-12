"""UFACTORY xArm7, seven joints, no gripper.

The USD is Isaac Sim 5.1's xArm7 asset with its gripper variant set to None,
taken from the Mimic repo (see assets/robots/xarm7/SOURCE.txt). It pins its
base to the world with its own `root_joint`, so the cfg does not fix it.
Gains and torque limits are left to the USD drives for now.
"""

from __future__ import annotations

import math

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg

from isaac_envs import ASSETS_ROOT

XARM7_USD = ASSETS_ROOT / "robots" / "xarm7" / "usd" / "ufactory_xarm7.usd"

ARM_JOINTS = [f"joint{i}" for i in range(1, 8)]
FLANGE_LINK = "link7"

XARM7_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=str(XARM7_USD),
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            max_depenetration_velocity=5.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False,
            solver_position_iteration_count=8,
            solver_velocity_iteration_count=0,
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        # Mimic's rest pose: the drive targets the USD ships with.
        joint_pos={
            "joint1": 0.0,
            "joint2": math.radians(-47.5),
            "joint3": 0.0,
            "joint4": 0.0,
            "joint5": 0.0,
            "joint6": 0.0,
            "joint7": math.radians(9.6),
        },
        joint_vel={".*": 0.0},
    ),
    actuators={
        # None keeps the USD's gains (stiffness about 2100-13000 N·m/rad on
        # joints 1-5) and max force (50 / 30 / 20 N·m on 1-2 / 3-5 / 6-7).
        "arm": ImplicitActuatorCfg(
            joint_names_expr=ARM_JOINTS,
            stiffness=None,
            damping=None,
        ),
    },
)
"""xArm7 on a fixed base, USD drive gains."""
