"""Robot articulation cfgs."""

from isaac_envs.robots.humanoid.g1 import G1_CFG
from isaac_envs.robots.hands.inspire_rh56bfx import INSPIRE_RH56BFX_CFG
from isaac_envs.robots.manipulation.so101 import SO101_CFG, SO101_HIGH_PD_CFG
from isaac_envs.robots.manipulation.xarm7 import XARM7_CFG
from isaac_envs.robots.manipulation.xarm7_inspire_rh56bfx import XARM7_INSPIRE_RH56BFX_CFG

__all__ = [
    "G1_CFG",
    "INSPIRE_RH56BFX_CFG",
    "SO101_CFG",
    "SO101_HIGH_PD_CFG",
    "XARM7_CFG",
    "XARM7_INSPIRE_RH56BFX_CFG",
]
