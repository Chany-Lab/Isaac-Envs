"""Convert a robot URDF to USD with Isaac Lab, then check the result.

    uv run python scripts/convert_urdf.py assets/robots/manipulation/so101/urdf/so101_new_calib.urdf \
        assets/robots/manipulation/so101/usd
    uv run python scripts/convert_urdf.py assets/robots/humanoid/g1/urdf/g1_29dof_rev_1_0.urdf \
        assets/robots/humanoid/g1/usd --floating-base --collider convex_hull

The options are fixed here rather than picked in the importer UI, so a
re-conversion gives the same USD. Drive gains written here are placeholders:
run scripts/write_drive_gains.py afterwards to copy the cfg's gains in.

Isaac Sim 6's URDF importer (3.0) names the output after the URDF and writes
`<out_dir>/<urdf name>/<urdf name>.usda`, always instanceable. The USDs in
assets/ were converted with Isaac Sim 5.1 (`<out_dir>/<name>.usd`); after a
re-conversion, point the robot cfg at the new file.

The check at the end catches the import traps hit before with Isaac Sim 5.1:
a stage whose metersPerUnit is not 1.0 (the robot flails on Play), and an
articulation PhysX cannot see (zero rigid bodies or joints).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
parser.add_argument("urdf", type=Path)
parser.add_argument("out_dir", type=Path)
parser.add_argument(
    "--keep-fixed-joints",
    action=argparse.BooleanOptionalAction,
    default=True,
    help="keep links on fixed joints (e.g. a TCP frame) instead of merging them",
)
parser.add_argument("--floating-base", action="store_true")
parser.add_argument(
    "--collider",
    choices=["convex_decomposition", "convex_hull"],
    default="convex_decomposition",
    help="convex_hull is coarser but much cheaper, e.g. for a humanoid in RL",
)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
args.headless = True
app = AppLauncher(args).app

from isaaclab.sim.converters import UrdfConverter, UrdfConverterCfg  # noqa: E402
from pxr import Usd, UsdGeom, UsdPhysics  # noqa: E402

COLLIDERS = {
    "convex_decomposition": "Convex Decomposition",
    "convex_hull": "Convex Hull",
}


def convert() -> Path:
    cfg = UrdfConverterCfg(
        asset_path=str(args.urdf.resolve()),
        usd_dir=str(args.out_dir.resolve()),
        force_usd_conversion=True,
        fix_base=not args.floating_base,
        merge_fixed_joints=not args.keep_fixed_joints,
        self_collision=False,
        collision_type=COLLIDERS[args.collider],
        joint_drive=UrdfConverterCfg.JointDriveCfg(
            drive_type="force",
            target_type="position",
            gains=UrdfConverterCfg.JointDriveCfg.PDGainsCfg(
                stiffness=17.8, damping=0.6
            ),
        ),
    )
    return Path(UrdfConverter(cfg).usd_path)


def check(usd_path: Path) -> list[str]:
    stage = Usd.Stage.Open(str(usd_path))
    problems = []
    meters = UsdGeom.GetStageMetersPerUnit(stage)
    if meters != 1.0:
        problems.append(f"metersPerUnit is {meters}, not 1.0")
    bodies, joints, roots = [], [], []
    for prim in stage.Traverse(Usd.TraverseInstanceProxies()):
        if prim.HasAPI(UsdPhysics.RigidBodyAPI):
            bodies.append(prim.GetName())
        if prim.IsA(UsdPhysics.RevoluteJoint) or prim.IsA(UsdPhysics.PrismaticJoint):
            joints.append(prim.GetName())
        if prim.HasAPI(UsdPhysics.ArticulationRootAPI):
            roots.append(str(prim.GetPath()))
    print(f"USD          {usd_path}")
    print(f"metersPerUnit {meters}, upAxis {UsdGeom.GetStageUpAxis(stage)}")
    print(f"articulation roots {roots}")
    print(f"rigid bodies ({len(bodies)}) {bodies}")
    print(f"moving joints ({len(joints)}) {joints}")
    if not roots:
        problems.append("no ArticulationRootAPI")
    if not bodies:
        problems.append("no rigid bodies")
    if not joints:
        problems.append("no revolute or prismatic joints")
    return problems


# Report before closing: SimulationApp.close() can end the process outright.
try:
    problems = check(convert())
    print("PROBLEMS: " + "; ".join(problems) if problems else "OK", flush=True)
finally:
    app.close()
sys.exit(1 if problems else 0)
