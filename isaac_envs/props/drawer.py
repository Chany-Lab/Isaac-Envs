"""Cabinet with one drawer. Front faces +x; joint `slide` is 0 closed,
`DRAWER_TRAVEL` fully open."""

from __future__ import annotations

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg

from isaac_envs import ASSETS_ROOT
from isaac_envs.props.dims import DRAWER_TRAVEL

DRAWER_USD = ASSETS_ROOT / "props" / "drawer" / "drawer.usd"

DRAWER_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=str(DRAWER_USD),
        # The USD pins the cabinet with its own root_joint.
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False,
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(joint_pos={"slide": 0.0}),
    actuators={
        # Passive: no spring, only damping, so the drawer stays where it is left.
        "slide": ImplicitActuatorCfg(
            joint_names_expr=["slide"],
            stiffness=0.0,
            damping=1.0,
            friction=0.05,
        ),
    },
)
"""Fixed cabinet whose drawer the robot can pull open and push shut."""

__all__ = ["DRAWER_CFG", "DRAWER_TRAVEL"]
