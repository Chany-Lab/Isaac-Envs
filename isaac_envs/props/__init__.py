"""Prop cfgs, one folder per prop: `<prop>/cfg.py`, and `<prop>/dims.py` for the
props `scripts/build_props.py` builds."""

from isaac_envs.props.cube import CUBE_CFG
from isaac_envs.props.desk import DESK_CFG
from isaac_envs.props.drawer import DRAWER_CFG
from isaac_envs.props.pan import PAN_CFG
from isaac_envs.props.pen import PEN_CFG
from isaac_envs.props.table import TABLE_CFG
from isaac_envs.props.tray import TRAY_CFG

__all__ = [
    "CUBE_CFG",
    "DESK_CFG",
    "DRAWER_CFG",
    "PAN_CFG",
    "PEN_CFG",
    "TABLE_CFG",
    "TRAY_CFG",
]
