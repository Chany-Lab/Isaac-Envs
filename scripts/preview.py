"""Load robot cfgs or a whole scene and leave everything at its init pose.

    uv run python scripts/preview.py SO101_CFG
    uv run python scripts/preview.py SO101_CFG SO101_HIGH_PD_CFG   # side by side
    uv run python scripts/preview.py --scene PEN_INTO_DRAWER_SCENE_CFG
    uv run python scripts/preview.py --scene PEN_INTO_DRAWER_SCENE_CFG --headless

Nothing is commanded: robots only hold their init pose.
"""

from __future__ import annotations

import argparse
import os

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("cfgs", nargs="*", help="names in isaac_envs.robots")
parser.add_argument("--scene", help="name in isaac_envs.scenes")
parser.add_argument("--spacing", type=float, default=0.5, help="metres between robots")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
if not args.cfgs and not args.scene:
    parser.error("give robot cfg names or --scene")
app = AppLauncher(args).app

import isaaclab.sim as sim_utils  # noqa: E402
from isaaclab.assets import Articulation  # noqa: E402
from isaaclab.scene import InteractiveScene  # noqa: E402

import isaac_envs.robots as robots  # noqa: E402
import isaac_envs.scenes as scenes  # noqa: E402

DT = 1.0 / 120.0


def robots_scene() -> dict[str, Articulation]:
    ground = sim_utils.GroundPlaneCfg()
    ground.func("/World/ground", ground)
    light = sim_utils.DomeLightCfg(intensity=2000.0)
    light.func("/World/light", light)
    loaded = {}
    for i, name in enumerate(args.cfgs):
        cfg = getattr(robots, name).replace(prim_path=f"/World/{name}")
        cfg.init_state.pos = (i * args.spacing, 0.0, 0.0)
        loaded[name] = Articulation(cfg)
    return loaded


def main() -> None:
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=DT))
    scene = InteractiveScene(getattr(scenes, args.scene)) if args.scene else None
    articulations = scene.articulations if scene else robots_scene()
    if scene:
        # Scenes centre the table on the env origin; look at its work side.
        sim.set_camera_view([0.4, 1.4, 1.6], [-0.3, 0.0, 0.75])
    else:
        sim.set_camera_view([0.9, 0.9, 0.9], [0.2, 0.0, 0.4])
    sim.reset()

    for name, art in articulations.items():
        print(f"{name}: {art.num_bodies} bodies, joints {art.joint_names}", flush=True)
    if scene:
        for name in scene.rigid_objects:
            print(f"{name}: rigid object", flush=True)
    if args.headless:
        return

    while app.is_running():
        for art in articulations.values():
            art.set_joint_position_target(art.data.default_joint_pos)
            art.write_data_to_sim()
        if scene:
            scene.write_data_to_sim()
        sim.step()
        if scene:
            scene.update(DT)
        else:
            for art in articulations.values():
                art.update(DT)


main()
if args.headless:
    # SimulationApp.close() can hang after a headless run.
    os._exit(0)
app.close()
