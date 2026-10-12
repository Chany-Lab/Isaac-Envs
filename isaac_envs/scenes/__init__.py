"""Scene cfgs: props placed together on the shared table, no task terms.

One folder per scene, `<scene>/cfg.py`, named for what happens in it, not for
the robot. Each scene fixes the SO-101 for now.
"""

from isaac_envs.scenes.pen_into_drawer import (
    PEN_INTO_DRAWER_SCENE_CFG,
    PenIntoDrawerSceneCfg,
)

__all__ = ["PEN_INTO_DRAWER_SCENE_CFG", "PenIntoDrawerSceneCfg"]
