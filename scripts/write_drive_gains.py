"""Write each robot cfg's actuator gains into its USD joint drives.

    uv run python scripts/write_drive_gains.py            # every robot
    uv run python scripts/write_drive_gains.py G1_CFG     # one robot

The cfgs in `isaac_envs/robots/` are the source of truth and Isaac Lab applies
them at spawn anyway. This copies them into the USD so the file alone (opened
in Isaac Sim, or used by another project) behaves the same. Run it again after
changing a cfg's gains or re-converting a URDF.

For each joint an actuator covers it writes stiffness, damping and, when the
cfg sets them, max force, max joint velocity and armature. They go into the
root layer of the cfg's USD as overrides, so the referenced layers stay as
they were. USD angular drives are per degree: stiffness and damping are
scaled by pi/180 and velocity limits converted to deg/s.
"""

from __future__ import annotations

import argparse
import math
import os
import re

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("cfgs", nargs="*", help="names in isaac_envs.robots")
args = parser.parse_args()
app = AppLauncher(headless=True).app

from pxr import PhysxSchema, Usd, UsdPhysics  # noqa: E402

import isaac_envs.robots as robots  # noqa: E402

# One cfg per USD: SO101_HIGH_PD_CFG shares SO101_CFG's file.
ROBOTS = ["SO101_CFG", "G1_CFG", "XARM7_CFG", "INSPIRE_RH56BFX_CFG"]


def per_joint(value, joint: str) -> float | None:
    """The value an actuator gives `joint`: a float, or a regex dict."""
    if value is None:
        return None
    if not isinstance(value, dict):
        return float(value)
    for expr, v in value.items():
        if re.fullmatch(expr, joint):
            return float(v)
    return None


def write(name: str) -> None:
    cfg = getattr(robots, name)
    stage = Usd.Stage.Open(cfg.spawn.usd_path)
    stage.SetEditTarget(stage.GetRootLayer())
    joints = {
        p.GetName(): p
        for p in stage.Traverse()
        if p.IsA(UsdPhysics.RevoluteJoint) or p.IsA(UsdPhysics.PrismaticJoint)
    }
    print(f"{name}: {cfg.spawn.usd_path}", flush=True)
    for actuator in cfg.actuators.values():
        names = [
            j
            for j in joints
            if any(re.fullmatch(e, j) for e in actuator.joint_names_expr)
        ]
        for joint in sorted(names):
            prim = joints[joint]
            angular = prim.IsA(UsdPhysics.RevoluteJoint)
            unit = math.pi / 180 if angular else 1.0
            drive = UsdPhysics.DriveAPI.Apply(prim, "angular" if angular else "linear")
            kp = per_joint(actuator.stiffness, joint)
            kd = per_joint(actuator.damping, joint)
            effort = per_joint(actuator.effort_limit_sim, joint)
            vel = per_joint(actuator.velocity_limit_sim, joint)
            arm = per_joint(actuator.armature, joint)
            if kp is not None:
                drive.CreateStiffnessAttr().Set(kp * unit)
            if kd is not None:
                drive.CreateDampingAttr().Set(kd * unit)
            if effort is not None:
                drive.CreateMaxForceAttr().Set(effort)
            physx = PhysxSchema.PhysxJointAPI.Apply(prim)
            if vel is not None:
                physx.CreateMaxJointVelocityAttr().Set(vel / unit)
            if arm is not None:
                physx.CreateArmatureAttr().Set(arm)
            print(
                f"  {joint:28s} kp {kp} kd {kd} effort {effort} vel {vel} armature {arm}",
                flush=True,
            )
    stage.GetRootLayer().Save()


for name in args.cfgs or ROBOTS:
    write(name)
# SimulationApp.close() can hang after a headless run.
os._exit(0)
