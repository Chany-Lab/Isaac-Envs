"""UFACTORY xArm7, seven joints, no gripper.

The USD is Isaac Sim 5.1's xArm7 asset with its gripper variant set to None,
taken from the Mimic repo (see assets/robots/manipulation/xarm7/SOURCE.txt). It pins its
base to the world with its own `root_joint`, so the cfg does not fix it.
Gains follow ManiSkill's xArm7 agent (stiffness 1e3, damping 1e2,
haosulab/ManiSkill, Apache-2.0); torque limits are UFACTORY's (50 / 30 / 20
N·m on joints 1-2 / 3-5 / 6-7), not ManiSkill's 500.
scripts/write_drive_gains.py writes the same values into the USD.
"""

from __future__ import annotations

import math

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg

from isaac_envs import ASSETS_ROOT

XARM7_USD = (
    ASSETS_ROOT
    / "robots"
    / "manipulation"
    / "xarm7"
    / "usd"
    / "ufactory_xarm7.usd"
)

ARM_JOINTS = [f"joint{i}" for i in range(1, 8)]
FLANGE_LINK = "link7"

XARM7_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=str(XARM7_USD),
        # The xArm controller compensates gravity, and ManiSkill's gains assume
        # it does; like Isaac Lab's Franka cfg, the arm ignores gravity instead.
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=True,
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
        "arm": ImplicitActuatorCfg(
            joint_names_expr=ARM_JOINTS,
            stiffness=1000.0,
            damping=100.0,
            effort_limit_sim={
                "joint[1-2]": 50.0,
                "joint[3-5]": 30.0,
                "joint[6-7]": 20.0,
            },
            velocity_limit_sim=3.14,  # 180 deg/s
        ),
    },
)
"""xArm7 on a fixed base, ManiSkill gains, UFACTORY torque limits."""
