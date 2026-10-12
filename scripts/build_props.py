"""Build the tabletop props as USD from boxes and cylinders.

    uv run python scripts/build_props.py

Writes assets/props/{table,pan,pen,drawer}/*.usd from the sizes in
isaac_envs/props/{table,pan,pen,drawer}/dims.py.
"""

from __future__ import annotations

import math
import os
from pathlib import Path

from isaaclab.app import AppLauncher

# pxr ships inside Isaac Sim and only imports once the app is up.
app = AppLauncher(headless=True).app

from pxr import Gf, Sdf, Usd, UsdGeom, UsdPhysics, UsdShade  # noqa: E402

from isaac_envs.props.drawer.dims import *  # noqa: E402,F403
from isaac_envs.props.pan.dims import *  # noqa: E402,F403
from isaac_envs.props.pen.dims import *  # noqa: E402,F403
from isaac_envs.props.table.dims import *  # noqa: E402,F403

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


def hex_prism(stage, path: str, length: float, width: float, center, color) -> None:
    """A hexagonal collider along x, flats at top and bottom: three boxes
    turned 0, 60 and 120 degrees about x. `width` is across the flats."""
    for i in range(3):
        cube = UsdGeom.Cube.Define(stage, f"{path}_{i}")
        cube.CreateSizeAttr(1.0)
        cube.AddTranslateOp().Set(Gf.Vec3d(*center))
        cube.AddRotateXOp().Set(60.0 * i)
        cube.AddScaleOp().Set(Gf.Vec3f(length, width / math.sqrt(3), width))
        cube.CreateDisplayColorAttr([Gf.Vec3f(*color)])
        UsdPhysics.CollisionAPI.Apply(cube.GetPrim())


def rigid_body(stage, path: str, mass: float) -> Usd.Prim:
    prim = UsdGeom.Xform.Define(stage, path).GetPrim()
    UsdPhysics.RigidBodyAPI.Apply(prim)
    UsdPhysics.MassAPI.Apply(prim).CreateMassAttr(mass)
    return prim


def build_table() -> Path:
    """Steel workbench, origin on the floor under the middle of the top.

    Legs sit in the corners and an apron frame runs under the top's edges;
    there is no shelf, so legs and knees fit under it.
    """
    path = PROPS / "table" / "table.usd"
    stage, root = new_stage(path, "table")
    top_grey = (0.62, 0.64, 0.66)
    frame_grey = (0.30, 0.31, 0.33)
    sx, sy = TABLE_SIZE
    box(
        stage,
        "/table/top",
        (sx, sy, TABLE_TOP),
        (0, 0, TABLE_HEIGHT - TABLE_TOP / 2),
        top_grey,
    )
    leg_h = TABLE_HEIGHT - TABLE_TOP
    lx, ly = sx / 2 - TABLE_LEG / 2, sy / 2 - TABLE_LEG / 2
    for i, (x, y) in enumerate([(1, 1), (1, -1), (-1, 1), (-1, -1)]):
        box(
            stage,
            f"/table/leg_{i}",
            (TABLE_LEG, TABLE_LEG, leg_h),
            (x * lx, y * ly, leg_h / 2),
            frame_grey,
        )
    ah, at = TABLE_APRON
    az = leg_h - ah / 2
    inner_x, inner_y = sx - 2 * TABLE_LEG, sy - 2 * TABLE_LEG
    for side in (1, -1):
        box(
            stage,
            f"/table/apron_x_{'pos' if side > 0 else 'neg'}",
            (inner_x, at, ah),
            (0, side * (ly + TABLE_LEG / 2 - at / 2), az),
            frame_grey,
        )
        box(
            stage,
            f"/table/apron_y_{'pos' if side > 0 else 'neg'}",
            (at, inner_y, ah),
            (side * (lx + TABLE_LEG / 2 - at / 2), 0, az),
            frame_grey,
        )
    bind_physics(root, physics_material(stage, "table", static=0.5, dynamic=0.4))
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


def build_pen() -> Path:
    """Ballpoint pen lying on a flat of its cap, tip along +x, origin under
    the middle of the pen."""
    path = PROPS / "pen" / "pen.usd"
    stage, root = new_stage(path, "pen")
    UsdPhysics.RigidBodyAPI.Apply(root)
    UsdPhysics.MassAPI.Apply(root).CreateMassAttr(PEN_MASS)
    # The cap is the widest part, so the pen rests on it.
    z = PEN_CAP_WIDTH / 2
    back = -PEN_LENGTH / 2
    tip_len, tip_r = PEN_TIP
    barrel = PEN_LENGTH - tip_len
    blue = (0.10, 0.20, 0.70)

    hex_prism(
        stage,
        "/pen/barrel",
        barrel,
        PEN_WIDTH,
        (back + barrel / 2, 0, z),
        (0.90, 0.90, 0.88),
    )
    hex_prism(
        stage,
        "/pen/cap",
        PEN_CAP_LENGTH,
        PEN_CAP_WIDTH,
        (back + PEN_CAP_LENGTH / 2, 0, z),
        blue,
    )
    cl, cw, ch = PEN_CLIP
    box(
        stage,
        "/pen/clip",
        (cl, cw, ch),
        (back + cl / 2 + 0.005, 0, PEN_CAP_WIDTH + ch / 2),
        blue,
    )
    tip = UsdGeom.Cylinder.Define(stage, "/pen/tip")
    tip.CreateRadiusAttr(tip_r)
    tip.CreateHeightAttr(tip_len)
    tip.CreateAxisAttr("X")
    tip.AddTranslateOp().Set(Gf.Vec3d(PEN_LENGTH / 2 - tip_len / 2, 0, z))
    tip.CreateDisplayColorAttr([Gf.Vec3f(0.6, 0.6, 0.6)])
    UsdPhysics.CollisionAPI.Apply(tip.GetPrim())

    bind_physics(root, physics_material(stage, "pen", static=0.6, dynamic=0.5))
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
    for build in (build_table, build_pan, build_pen, build_drawer):
        print(build(), flush=True)
    # SimulationApp.close() can hang after a headless run.
    os._exit(0)
