"""Pen into drawer: a ballpoint pen and a drawer cabinet on the shared steel
table, with a robot at the table's -x edge.

The scene does not belong to one robot. The env origin is on the floor under
the middle of the table, and props are placed from the work point
`WORK_POS`: the spot on the table top the robot works around, 0.15 m in from
the -x edge. For now the robot is the SO-101, mounted on the top at
`WORK_POS` and facing +x. Only placement lives here: tasks add their own
terms.
"""

from __future__ import annotations

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg, AssetBaseCfg, RigidObjectCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.utils import configclass

from isaac_envs.props import DRAWER_CFG, PEN_CFG, TABLE_CFG
from isaac_envs.props.table import TABLE_HEIGHT, TABLE_SIZE
from isaac_envs.robots import SO101_CFG

H = TABLE_HEIGHT
WORK_POS = (-TABLE_SIZE[0] / 2 + 0.15, 0.0, H)

# Yaw quaternions, (w, x, y, z).
YAW_MINUS_90 = (0.7071068, 0.0, 0.0, -0.7071068)
YAW_180 = (0.0, 0.0, 0.0, 1.0)


def on_table(dx: float, dy: float) -> tuple[float, float, float]:
    """A point on the table top, `dx` ahead of and `dy` left of `WORK_POS`."""
    return (WORK_POS[0] + dx, WORK_POS[1] + dy, H)


@configclass
class PenIntoDrawerSceneCfg(InteractiveSceneCfg):
    ground = AssetBaseCfg(
        prim_path="/World/ground",
        spawn=sim_utils.GroundPlaneCfg(),
        collision_group=-1,
    )
    light = AssetBaseCfg(
        prim_path="/World/light",
        spawn=sim_utils.DomeLightCfg(intensity=2000.0),
    )

    table: AssetBaseCfg = TABLE_CFG.replace(prim_path="{ENV_REGEX_NS}/Table")
    # Fixed to the SO-101 for now; another robot replaces this field.
    robot: ArticulationCfg = SO101_CFG.replace(
        prim_path="{ENV_REGEX_NS}/Robot",
        init_state=SO101_CFG.init_state.replace(pos=WORK_POS),
    )
    # Front right, lying across the robot's view with the tip to -y, so the
    # jaws close across the barrel.
    pen: RigidObjectCfg = PEN_CFG.replace(
        prim_path="{ENV_REGEX_NS}/Pen",
        init_state=RigidObjectCfg.InitialStateCfg(
            pos=on_table(0.20, -0.14), rot=YAW_MINUS_90
        ),
    )
    # Front left, drawer front facing the robot.
    drawer: ArticulationCfg = DRAWER_CFG.replace(
        prim_path="{ENV_REGEX_NS}/Drawer",
        init_state=DRAWER_CFG.init_state.replace(pos=on_table(0.30, 0.17), rot=YAW_180),
    )


PEN_INTO_DRAWER_SCENE_CFG = PenIntoDrawerSceneCfg(num_envs=1, env_spacing=2.5)
"""One env; labs set num_envs themselves with `.replace(num_envs=...)`."""
