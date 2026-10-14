"""Lift a cube: a red cube 28 cm in front of the robot at the edge of a table, a tray to its right.

Shared with Interface, which lists it read-only next to its own environments; tag it with a
robot on Interface's Environments page (e.g. so101_follower, from sims/robots/).
"""

TABLE_TOP = 0.75  # assets/props/desk surface height (m)


def build(scene):
    scene.add("desk")
    scene.add("cube", pos=(0, 0.08, TABLE_TOP))
    scene.add("tray", pos=(0.2, 0.0, TABLE_TOP))
    # SO-101 faces +X in its own frame; yaw 90 turns it toward the cube
    scene.robot(pos=(0, -0.2, TABLE_TOP), yaw=90)
