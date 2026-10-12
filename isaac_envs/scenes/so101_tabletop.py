"""SO-101 on a table with a pan and a drawer cabinet in reach.

Positions are in the env frame; the robot base sits on the table top at the
origin, facing +x. Only placement lives here: tasks add their own terms.
"""

from __future__ import annotations

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg, AssetBaseCfg, RigidObjectCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.utils import configclass

from isaac_envs.props import DRAWER_CFG, PAN_CFG, TABLE_CFG
from isaac_envs.props.dims import TABLE_HEIGHT
from isaac_envs.robots import SO101_CFG

H = TABLE_HEIGHT

# Yaw quaternions, (w, x, y, z).
YAW_MINUS_90 = (0.7071068, 0.0, 0.0, -0.7071068)
YAW_180 = (0.0, 0.0, 0.0, 1.0)


@configclass
class SO101TabletopSceneCfg(InteractiveSceneCfg):
    ground = AssetBaseCfg(
        prim_path="/World/ground",
        spawn=sim_utils.GroundPlaneCfg(),
        collision_group=-1,
    )
    light = AssetBaseCfg(
        prim_path="/World/light",
        spawn=sim_utils.DomeLightCfg(intensity=2000.0),
    )

    # The table reaches 0.15 m behind the robot and 0.65 m in front.
    table: AssetBaseCfg = TABLE_CFG.replace(
        prim_path="{ENV_REGEX_NS}/Table",
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0.25, 0.0, 0.0)),
    )
    robot: ArticulationCfg = SO101_CFG.replace(
        prim_path="{ENV_REGEX_NS}/Robot",
        init_state=SO101_CFG.init_state.replace(pos=(0.0, 0.0, H)),
    )
    # Front right, handle pointing away to -y.
    pan: RigidObjectCfg = PAN_CFG.replace(
        prim_path="{ENV_REGEX_NS}/Pan",
        init_state=RigidObjectCfg.InitialStateCfg(
            pos=(0.20, -0.14, H), rot=YAW_MINUS_90
        ),
    )
    # Front left, drawer front facing the robot.
    drawer: ArticulationCfg = DRAWER_CFG.replace(
        prim_path="{ENV_REGEX_NS}/Drawer",
        init_state=DRAWER_CFG.init_state.replace(pos=(0.30, 0.17, H), rot=YAW_180),
    )


SO101_TABLETOP_SCENE_CFG = SO101TabletopSceneCfg(num_envs=1, env_spacing=2.0)
"""One env; labs set num_envs themselves with `.replace(num_envs=...)`."""
