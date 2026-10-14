"""Render the thumbnails in Envs.md and Objects.md into media/.

    uv run python scripts/capture.py --headless --enable_cameras

Each prop sits on the ground away from the scene, and one camera visits every
shot. Props hold their init pose; the drawer is pulled half open so it reads
as a drawer.
"""

from __future__ import annotations

import argparse
import os

from isaaclab.app import add_launcher_args, launch_simulation

parser = argparse.ArgumentParser()
parser.add_argument("--size", type=int, default=512, help="image width and height")
# Kept from Isaac Lab 2.x: 3.0 always runs headless here and the camera turns
# rendering on by itself.
parser.add_argument("--headless", action="store_true", help=argparse.SUPPRESS)
parser.add_argument("--enable_cameras", action="store_true", help=argparse.SUPPRESS)
add_launcher_args(parser)
args = parser.parse_args()
args.headless = True
args.enable_cameras = True

import isaaclab.sim as sim_utils  # noqa: E402
from isaaclab_physx.physics import PhysxCfg  # noqa: E402

from isaac_envs import REPO_ROOT  # noqa: E402

DT = 1.0 / 120.0
SIM_CFG = sim_utils.SimulationCfg(dt=DT, device=args.device, physics=PhysxCfg())
OUT = REPO_ROOT / "media"

# Props stand in a row at y = -10 m, out of the scene's view.
PEN_POS = (0.0, -10.0, 0.0)
PAN_POS = (2.0, -10.0, 0.0)
DRAWER_POS = (4.0, -10.0, 0.0)
CUBE_POS = (6.0, -10.0, 0.0)
TRAY_POS = (8.0, -10.0, 0.0)
DESK_POS = (11.0, -10.0, 0.0)


def add(pos, offset):
    return [p + o for p, o in zip(pos, offset)]


# name: (eye, target)
SHOTS = {
    "pen": (add(PEN_POS, (0.10, 0.14, 0.12)), add(PEN_POS, (0.0, 0.0, 0.005))),
    "pan": (add(PAN_POS, (0.16, 0.22, 0.22)), add(PAN_POS, (0.03, 0.0, 0.01))),
    "drawer": (add(DRAWER_POS, (0.45, 0.35, 0.35)), add(DRAWER_POS, (0.05, 0.0, 0.06))),
    "cube": (add(CUBE_POS, (0.09, 0.11, 0.10)), add(CUBE_POS, (0.0, 0.0, 0.02))),
    "tray": (add(TRAY_POS, (0.18, 0.22, 0.22)), add(TRAY_POS, (0.0, 0.0, 0.01))),
    "desk": (add(DESK_POS, (1.6, 1.9, 1.6)), add(DESK_POS, (0.0, 0.0, 0.4))),
    "pen_into_drawer": ([-0.75, -0.55, 1.55], [0.0, 0.0, 1.0]),
}


def main() -> None:
    # Asset modules load USD (pxr); Kit must be up first.
    import torch
    from isaaclab.assets import Articulation, RigidObject, RigidObjectCfg
    from isaaclab.scene import InteractiveScene
    from isaaclab.sensors import Camera, CameraCfg
    from isaaclab_physx.renderers import IsaacRtxRendererCfg
    from PIL import Image

    from isaac_envs.props import (
        CUBE_CFG,
        DESK_CFG,
        DRAWER_CFG,
        PAN_CFG,
        PEN_CFG,
        TRAY_CFG,
    )
    from isaac_envs.props.drawer import DRAWER_TRAVEL
    from isaac_envs.scenes import PEN_INTO_DRAWER_SCENE_CFG

    sim = sim_utils.SimulationContext(SIM_CFG)
    scene = InteractiveScene(PEN_INTO_DRAWER_SCENE_CFG)
    pen = RigidObject(
        PEN_CFG.replace(
            prim_path="/World/Pen",
            init_state=RigidObjectCfg.InitialStateCfg(pos=PEN_POS),
        )
    )
    pan = RigidObject(
        PAN_CFG.replace(
            prim_path="/World/Pan",
            init_state=RigidObjectCfg.InitialStateCfg(pos=PAN_POS),
        )
    )
    drawer = Articulation(
        DRAWER_CFG.replace(
            prim_path="/World/Drawer",
            init_state=DRAWER_CFG.init_state.replace(
                pos=DRAWER_POS, joint_pos={"slide": DRAWER_TRAVEL / 2}
            ),
        )
    )
    cube = RigidObject(
        CUBE_CFG.replace(
            prim_path="/World/Cube",
            init_state=RigidObjectCfg.InitialStateCfg(pos=CUBE_POS),
        )
    )
    # Static props: spawned as they are, nothing to update.
    for name, cfg, pos in (("Tray", TRAY_CFG, TRAY_POS), ("Desk", DESK_CFG, DESK_POS)):
        cfg.spawn.func(f"/World/{name}", cfg.spawn, translation=pos)
    camera = Camera(
        CameraCfg(
            prim_path="/World/Camera",
            width=args.size,
            height=args.size,
            data_types=["rgb"],
            spawn=sim_utils.PinholeCameraCfg(focal_length=24.0),
            # The camera sits outside the envs; RTX per-env partitioning
            # would hide the scene from it.
            renderer_cfg=IsaacRtxRendererCfg(enable_scene_partitioning=False),
        )
    )
    sim.reset()
    for art in [*scene.articulations.values(), drawer]:
        art.write_joint_position_to_sim_index(position=art.data.default_joint_pos.torch)
        art.write_joint_velocity_to_sim_index(velocity=art.data.default_joint_vel.torch)

    OUT.mkdir(exist_ok=True)
    for name, (eye, target) in SHOTS.items():
        camera.set_world_poses_from_view(
            torch.tensor([eye], device=sim.device),
            torch.tensor([target], device=sim.device),
        )
        # The renderer needs a few frames to settle after the camera moves.
        for _ in range(30):
            for art in [*scene.articulations.values(), drawer]:
                art.actuators.target_command.set_position_index(
                    value=art.data.default_joint_pos.torch
                )
                art.write_data_to_sim()
            sim.step()
            scene.update(DT)
            for asset in (pen, pan, drawer, cube):
                asset.update(DT)
        camera.update(DT)
        rgb = camera.data.output["rgb"].torch[0, ..., :3].cpu().numpy()
        Image.fromarray(rgb).save(OUT / f"{name}.png")
        print(f"wrote media/{name}.png", flush=True)


with launch_simulation(SIM_CFG, args):
    main()
    # Closing Kit can hang after a headless run.
    os._exit(0)
