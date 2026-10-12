"""Build the tabletop props as USD from boxes and cylinders.

    uv run python scripts/build_props.py

Writes assets/props/{table,pan,drawer}/*.usd from the sizes in
isaac_envs/props/dims.py.
"""

from __future__ import annotations

import math
import os
from pathlib import Path

from isaaclab.app import AppLauncher

# pxr ships inside Isaac Sim and only imports once the app is up.
app = AppLauncher(headless=True).app

from pxr import Gf, Sdf, Usd, UsdGeom, UsdPhysics, UsdShade  # noqa: E402

from isaac_envs.props.dims import *  # noqa: E402,F403

PROPS = Path(__file__).resolve().parents[1] / "assets" / "props"


def new_stage(path: Path, root: str) -> tuple[Usd.Stage, Usd.Prim]:
    path.parent.mkdir(parents=True, exist_ok=True)
    stage = Usd.Stage.CreateNew(str(path))
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    prim = UsdGeom.Xform.Define(stage, f"/{root}").GetPrim()
    stage.SetDefaultPrim(prim)
    return stage, prim


def physics_material(stage, root: str, static=0.8, dynamic=0.6) -> UsdShade.Material:
    material = UsdShade.Material.Define(stage, f"/{root}/physics_material")
    api = UsdPhysics.MaterialAPI.Apply(material.GetPrim())
    api.CreateStaticFrictionAttr(static)
    api.CreateDynamicFrictionAttr(dynamic)
    api.CreateRestitutionAttr(0.0)
    return material


def bind_physics(prim, material) -> None:
    UsdShade.MaterialBindingAPI.Apply(prim).Bind(
        material, UsdShade.Tokens.weakerThanDescendants, "physics"
    )


def box(stage, path: str, size, center, color) -> None:
    """A collider box: a unit cube scaled to `size`, centred at `center`."""
    cube = UsdGeom.Cube.Define(stage, path)
    cube.CreateSizeAttr(1.0)
    cube.AddTranslateOp().Set(Gf.Vec3d(*center))
    cube.AddScaleOp().Set(Gf.Vec3f(*size))
    cube.CreateDisplayColorAttr([Gf.Vec3f(*color)])
    UsdPhysics.CollisionAPI.Apply(cube.GetPrim())


def rigid_body(stage, path: str, mass: float) -> Usd.Prim:
    prim = UsdGeom.Xform.Define(stage, path).GetPrim()
    UsdPhysics.RigidBodyAPI.Apply(prim)
    UsdPhysics.MassAPI.Apply(prim).CreateMassAttr(mass)
    return prim


def build_table() -> Path:
    path = PROPS / "table" / "table.usd"
    stage, root = new_stage(path, "table")
    wood = (0.55, 0.40, 0.25)
    sx, sy = TABLE_SIZE
    box(
        stage,
        "/table/top",
        (sx, sy, TABLE_TOP),
        (0, 0, TABLE_HEIGHT - TABLE_TOP / 2),
        wood,
    )
    leg_h = TABLE_HEIGHT - TABLE_TOP
    for i, (x, y) in enumerate([(1, 1), (1, -1), (-1, 1), (-1, -1)]):
        center = (x * (sx / 2 - TABLE_LEG), y * (sy / 2 - TABLE_LEG), leg_h / 2)
        box(stage, f"/table/leg_{i}", (TABLE_LEG, TABLE_LEG, leg_h), center, wood)
    bind_physics(root, physics_material(stage, "table"))
    stage.Save()
    return path


def build_pan() -> Path:
    """Pan centred on its base, handle along +x."""
    path = PROPS / "pan" / "pan.usd"
    stage, root = new_stage(path, "pan")
    UsdPhysics.RigidBodyAPI.Apply(root)
    UsdPhysics.MassAPI.Apply(root).CreateMassAttr(PAN_MASS)
    steel = (0.20, 0.20, 0.22)
    t = PAN_THICKNESS

    bottom = UsdGeom.Cylinder.Define(stage, "/pan/bottom")
    bottom.CreateRadiusAttr(PAN_RADIUS)
    bottom.CreateHeightAttr(t)
    bottom.CreateAxisAttr("Z")
    bottom.AddTranslateOp().Set(Gf.Vec3d(0, 0, t / 2))
    bottom.CreateDisplayColorAttr([Gf.Vec3f(*steel)])
    UsdPhysics.CollisionAPI.Apply(bottom.GetPrim())

    # The wall is a ring of boxes: a concave mesh would need decomposition.
    seg = 2 * math.pi * PAN_RADIUS / PAN_WALL_SEGMENTS * 1.05
    for i in range(PAN_WALL_SEGMENTS):
        a = 2 * math.pi * i / PAN_WALL_SEGMENTS
        r = PAN_RADIUS - t / 2
        cube = UsdGeom.Cube.Define(stage, f"/pan/wall_{i:02d}")
        cube.CreateSizeAttr(1.0)
        cube.AddTranslateOp().Set(
            Gf.Vec3d(r * math.cos(a), r * math.sin(a), PAN_WALL_HEIGHT / 2)
        )
        cube.AddRotateZOp().Set(math.degrees(a))
        cube.AddScaleOp().Set(Gf.Vec3f(t, seg, PAN_WALL_HEIGHT))
        cube.CreateDisplayColorAttr([Gf.Vec3f(*steel)])
        UsdPhysics.CollisionAPI.Apply(cube.GetPrim())

    hl, hw, hh = PAN_HANDLE
    box(
        stage,
        "/pan/handle",
        (hl, hw, hh),
        (PAN_RADIUS + hl / 2, 0, PAN_WALL_HEIGHT - hh / 2),
        (0.08, 0.08, 0.08),
    )
    bind_physics(root, physics_material(stage, "pan"))
    stage.Save()
    return path


def build_drawer() -> Path:
    """Cabinet with one drawer. Front faces +x, the drawer slides out along +x.

    Joint `slide` is 0 when closed and DRAWER_TRAVEL when fully open.
    """
    path = PROPS / "drawer" / "drawer.usd"
    stage, root = new_stage(path, "drawer")
    cx, cy, cz = CABINET
    w = CABINET_WALL
    white = (0.85, 0.85, 0.82)

    rigid_body(stage, "/drawer/cabinet", CABINET_MASS)
    # Pin the cabinet to the world and root the articulation on that joint,
    # as the URDF importer does for robots; Isaac Lab's fix_root_link needs
    # a rigid body on the top prim instead.
    anchor = UsdPhysics.FixedJoint.Define(stage, "/drawer/root_joint")
    anchor.CreateBody1Rel().SetTargets([Sdf.Path("/drawer/cabinet")])
    UsdPhysics.ArticulationRootAPI.Apply(anchor.GetPrim())
    panels = {
        "top": ((cx, cy, w), (0, 0, cz - w / 2)),
        "bottom": ((cx, cy, w), (0, 0, w / 2)),
        "left": ((cx, w, cz - 2 * w), (0, cy / 2 - w / 2, cz / 2)),
        "right": ((cx, w, cz - 2 * w), (0, -cy / 2 + w / 2, cz / 2)),
        "back": ((w, cy - 2 * w, cz - 2 * w), (-cx / 2 + w / 2, 0, cz / 2)),
    }
    for name, (size, center) in panels.items():
        box(stage, f"/drawer/cabinet/{name}", size, center, white)

    # Drawer box, built around its own origin at the centre of its floor.
    c = DRAWER_CLEARANCE
    dx = cx - w - c
    dy = cy - 2 * w - 2 * c
    dz = cz - 2 * w - 2 * c
    t = DRAWER_WALL
    rigid_body(stage, "/drawer/tray", DRAWER_MASS)
    wood = (0.60, 0.45, 0.30)
    tray = {
        "floor": ((dx, dy, t), (0, 0, t / 2)),
        "front": ((t, dy, dz), (dx / 2 - t / 2, 0, dz / 2)),
        "back": ((t, dy, dz * 0.8), (-dx / 2 + t / 2, 0, dz * 0.4)),
        "left": ((dx - 2 * t, t, dz * 0.8), (0, dy / 2 - t / 2, dz * 0.4)),
        "right": ((dx - 2 * t, t, dz * 0.8), (0, -dy / 2 + t / 2, dz * 0.4)),
    }
    for name, (size, center) in tray.items():
        box(stage, f"/drawer/tray/{name}", size, center, wood)
    hx, hy, hz = DRAWER_HANDLE
    box(
        stage,
        "/drawer/tray/handle",
        (hx, hy, hz),
        (dx / 2 + hx / 2, 0, dz * 0.6),
        (0.1, 0.1, 0.1),
    )

    # Closed: the tray front sits flush with the cabinet front.
    closed = Gf.Vec3f(cx / 2 - dx / 2, 0, w + c)
    tray_prim = stage.GetPrimAtPath("/drawer/tray")
    UsdGeom.Xformable(tray_prim).AddTranslateOp().Set(Gf.Vec3d(*closed))

    joint = UsdPhysics.PrismaticJoint.Define(stage, "/drawer/slide")
    joint.CreateBody0Rel().SetTargets([Sdf.Path("/drawer/cabinet")])
    joint.CreateBody1Rel().SetTargets([Sdf.Path("/drawer/tray")])
    joint.CreateAxisAttr("X")
    joint.CreateLocalPos0Attr(closed)
    joint.CreateLocalPos1Attr(Gf.Vec3f(0, 0, 0))
    joint.CreateLowerLimitAttr(0.0)
    joint.CreateUpperLimitAttr(DRAWER_TRAVEL)

    bind_physics(root, physics_material(stage, "drawer", static=0.6, dynamic=0.5))
    stage.Save()
    return path


if __name__ == "__main__":
    for build in (build_table, build_pan, build_drawer):
        print(build(), flush=True)
    # SimulationApp.close() can hang after a headless run.
    os._exit(0)
