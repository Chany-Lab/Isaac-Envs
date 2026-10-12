"""Spawn a robot cfg and check its physics: hold the init pose, then step
each joint alone both ways and back.

    python scripts/preview.py SO101_CFG --headless
    python scripts/preview.py SO101_HIGH_PD_CFG        # with the viewer
"""

from __future__ import annotations

import argparse
import os

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("cfg", help="name in isaac_envs.robots, e.g. SO101_CFG")
parser.add_argument("--hold-s", type=float, default=2.0)
parser.add_argument("--track-s", type=float, default=1.5)
parser.add_argument("--fraction", type=float, default=0.5, help="share of half-range")
parser.add_argument("--no-ground", action="store_true")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
app = AppLauncher(args).app

import torch  # noqa: E402

import isaaclab.sim as sim_utils  # noqa: E402
from isaaclab.assets import Articulation  # noqa: E402

import isaac_envs.robots as robots  # noqa: E402

DT = 1.0 / 120.0
RUNAWAY_RAD_S = 50.0
DEG = 57.2958


def run(sim, robot, target, seconds) -> float:
    """Step toward `target`; return the peak joint speed seen."""
    peak = 0.0
    for _ in range(int(seconds / DT)):
        robot.set_joint_position_target(target)
        robot.write_data_to_sim()
        sim.step(render=not args.headless)
        robot.update(DT)
        peak = max(peak, robot.data.joint_vel.abs().max().item())
    return peak


def main() -> bool:
    cfg = getattr(robots, args.cfg).replace(prim_path="/World/Robot")
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=DT))
    if not args.no_ground:
        sim_utils.GroundPlaneCfg().func("/World/ground", sim_utils.GroundPlaneCfg())
    light = sim_utils.DomeLightCfg(intensity=2000.0)
    light.func("/World/light", light)
    robot = Articulation(cfg)
    sim.set_camera_view([0.6, 0.6, 0.5], [0.0, 0.0, 0.2])
    sim.reset()

    names = robot.joint_names
    lower, upper = robot.data.soft_joint_pos_limits[0].unbind(-1)
    init = robot.data.default_joint_pos.clone()
    print(f"cfg {args.cfg}, ground {not args.no_ground}, joints {names}")

    peak = run(sim, robot, init, args.hold_s)
    print(f"\nhold init pose {args.hold_s}s (error, deg)")
    hold = (robot.data.joint_pos - init)[0] * DEG
    for name, e in zip(names, hold.tolist()):
        print(f"  {name:14s} {e:+7.2f}")

    print(f"\ntrack one joint at a time, {args.fraction:.0%} of half-range")
    worst = 0.0
    for j, name in enumerate(names):
        row = []
        for sign in (1.0, -1.0):
            target = init.clone()
            half = (upper[j] - lower[j]) / 2
            target[0, j] = (lower[j] + upper[j]) / 2 + sign * args.fraction * half
            peak = max(peak, run(sim, robot, target, args.track_s))
            err = (robot.data.joint_pos[0, j] - target[0, j]).item() * DEG
            worst = max(worst, abs(err))
            row.append(f"{target[0, j].item() * DEG:+7.1f} -> err {err:+7.2f}")
            peak = max(peak, run(sim, robot, init, args.track_s))
        print(f"  {name:14s} " + " | ".join(row))

    finite = bool(torch.isfinite(robot.data.joint_pos).all())
    stable = finite and peak < RUNAWAY_RAD_S
    print(f"\npeak speed {peak:.2f} rad/s, finite {finite}")
    print(
        f"max hold error {hold.abs().max().item():.2f} deg, max track {worst:.2f} deg"
    )
    print(f"RESULT: {'STABLE' if stable else 'UNSTABLE'}", flush=True)

    while not args.headless and app.is_running():
        run(sim, robot, init, 1.0)
    return stable


ok = main()
if args.headless:
    # SimulationApp.close() can hang after a headless run; nothing is left
    # to save, so leave without it.
    os._exit(0 if ok else 1)
app.close()
