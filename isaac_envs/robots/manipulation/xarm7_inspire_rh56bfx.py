"""xArm7 with the right Inspire RH56BFX hand fixed to its flange (link7).

The USD (taken from Mimic, see assets/robots/manipulation/xarm7_inspire_rh56bfx/SOURCE.txt)
references this repo's xArm7 and Inspire wrapper and joins them with a
FixedJoint, so it gets the same thumb limit fix and drive gains. The arm keeps
its own root_joint to the world. Actuators are the two robots' cfgs together.
"""

from __future__ import annotations

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg

from isaac_envs import ASSETS_ROOT
from isaac_envs.robots.hands.inspire_rh56bfx import HAND_JOINTS, INSPIRE_RH56BFX_CFG
from isaac_envs.robots.manipulation.xarm7 import ARM_JOINTS, XARM7_CFG

XARM7_INSPIRE_RH56BFX_USD = (
    ASSETS_ROOT
    / "robots"
    / "manipulation"
    / "xarm7_inspire_rh56bfx"
    / "usd"
    / "xarm7_inspire_rh56bfx.usda"
)

PALM_LINK = "palm"

XARM7_INSPIRE_RH56BFX_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=str(XARM7_INSPIRE_RH56BFX_USD),
        # Gravity off, as for the xArm7 alone: its controller compensates it.
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=True,
            max_depenetration_velocity=1.0,
        ),
        # The hand's small links need the hand's solver iterations.
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False,
            solver_position_iteration_count=16,
            solver_velocity_iteration_count=1,
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        # Arm in the xArm7's rest pose, hand open.
        joint_pos={**XARM7_CFG.init_state.joint_pos, "right_.*": 0.0},
        joint_vel={".*": 0.0},
    ),
    actuators={
        "arm": XARM7_CFG.actuators["arm"].replace(joint_names_expr=ARM_JOINTS),
        "fingers": INSPIRE_RH56BFX_CFG.actuators["fingers"].replace(
            joint_names_expr=HAND_JOINTS
        ),
    },
)
"""xArm7 with the Inspire hand, fixed base, both robots' gains."""
