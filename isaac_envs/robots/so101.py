"""SO-101 follower arm (six Feetech STS3215).

* `SO101_CFG`: gains from the official STS3215 identification
  (`joints_properties.xml`), limits from the 7.4 V datasheet.
* `SO101_HIGH_PD_CFG`: stiff gains from isaac_so_arm101 for tight tracking.

The URDF's effort/velocity of 10 are placeholders; the actuators override them.
"""

from __future__ import annotations

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg

from isaac_envs import ASSETS_ROOT

SO101_USD = ASSETS_ROOT / "robots" / "so101" / "usd" / "so101.usd"

ARM_JOINTS = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"]
GRIPPER_JOINT = "gripper"
TCP_LINK = "gripper_frame_link"

STS3215_STALL_NM = 1.91  # 7.4 V
STS3215_SPEED_RAD_S = 5.45  # 52 rpm, no load

SO101_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=str(SO101_USD),
        activate_contact_sensors=False,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            max_depenetration_velocity=5.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=True,
            solver_position_iteration_count=8,
            solver_velocity_iteration_count=0,
            fix_root_link=True,
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        # Upright with the wrist folded forward, as in isaac_so_arm101; all
        # zeros points the gripper straight up.
        joint_pos={
            "shoulder_pan": 0.0,
            "shoulder_lift": 0.0,
            "elbow_flex": 0.0,
            "wrist_flex": 1.57,
            "wrist_roll": 0.0,
            "gripper": 0.0,
        },
        joint_vel={".*": 0.0},
    ),
    actuators={
        "arm": ImplicitActuatorCfg(
            joint_names_expr=ARM_JOINTS,
            stiffness=17.8,
            damping=0.60,
            armature=0.028,
            friction=0.052,
            effort_limit_sim=STS3215_STALL_NM,
            velocity_limit_sim=STS3215_SPEED_RAD_S,
        ),
        "gripper": ImplicitActuatorCfg(
            joint_names_expr=[GRIPPER_JOINT],
            stiffness=17.8,
            damping=0.60,
            armature=0.028,
            friction=0.052,
            effort_limit_sim=STS3215_STALL_NM,
            velocity_limit_sim=STS3215_SPEED_RAD_S,
        ),
    },
    soft_joint_pos_limit_factor=1.0,
)
"""SO-101 with the identified STS3215 dynamics and datasheet limits."""


SO101_HIGH_PD_CFG = SO101_CFG.copy()
SO101_HIGH_PD_CFG.actuators["arm"].stiffness = {
    "shoulder_pan": 200.0,
    "shoulder_lift": 170.0,
    "elbow_flex": 120.0,
    "wrist_flex": 80.0,
    "wrist_roll": 50.0,
}
SO101_HIGH_PD_CFG.actuators["arm"].damping = {
    "shoulder_pan": 80.0,
    "shoulder_lift": 65.0,
    "elbow_flex": 45.0,
    "wrist_flex": 30.0,
    "wrist_roll": 20.0,
}
SO101_HIGH_PD_CFG.actuators["gripper"].stiffness = 60.0
SO101_HIGH_PD_CFG.actuators["gripper"].damping = 20.0
"""SO-101 with stiff PD gains (isaac_so_arm101) for tight joint tracking."""
