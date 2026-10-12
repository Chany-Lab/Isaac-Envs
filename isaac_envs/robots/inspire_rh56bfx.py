"""Inspire RH56BFX dexterous hand, right, on its own.

The USD is Isaac Sim 6.0's Inspire rigging sample, taken from the Mimic repo
(see assets/robots/inspire_rh56bfx/SOURCE.txt), loaded through
`inspire_rh56bfx_isaaclab.usda`, which switches off the sample's own
PhysicsScene and its world FixedJoint. The cfg fixes the root link instead, so
the hand stands alone wherever it is placed; mounting it on an arm means
composing the two USDs.

Six joints are driven: thumb swing and bend, and the first joint of each
finger. The other finger joints follow them through PhysX mimic joints and
have no drive, so no actuator covers them.
"""

from __future__ import annotations

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg

from isaac_envs import ASSETS_ROOT

INSPIRE_RH56BFX_USD = (
    ASSETS_ROOT / "robots" / "inspire_rh56bfx" / "usd" / "inspire_rh56bfx_isaaclab.usda"
)

HAND_JOINTS = [
    "right_thumb_1_joint",
    "right_thumb_2_joint",
    "right_index_1_joint",
    "right_middle_1_joint",
    "right_ring_1_joint",
    "right_little_1_joint",
]

INSPIRE_RH56BFX_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=str(INSPIRE_RH56BFX_USD),
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            max_depenetration_velocity=1.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False,
            solver_position_iteration_count=16,
            solver_velocity_iteration_count=1,
            fix_root_link=True,
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        joint_pos={".*": 0.0}, joint_vel={".*": 0.0}
    ),
    actuators={
        # None keeps the USD's gains and force limits (1.4-1.9 N·m).
        "fingers": ImplicitActuatorCfg(
            joint_names_expr=HAND_JOINTS,
            stiffness=None,
            damping=None,
        ),
    },
)
"""Right Inspire hand, open, root fixed where it is placed, USD drive gains."""
