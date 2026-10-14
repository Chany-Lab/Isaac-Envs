# Envs

Scene cfgs built from the robots and [objects](Objects.md) in this repo.

<br>

### Available Envs

| Img | Env | Model Name | Robot | Objects |
| :---: | :--- | :--- | :--- | :--- |
| <img src="media/pen_into_drawer.png" width="120"> | Pen into drawer | `PEN_INTO_DRAWER_SCENE_CFG` | SO-101 | Table, Pen, Drawer |

```python
from isaac_envs.scenes import PEN_INTO_DRAWER_SCENE_CFG

scene = PEN_INTO_DRAWER_SCENE_CFG.replace(num_envs=64)
```

Scenes are named after the task, not the robot. Swap the `robot` field to use
another robot.

<br>

### Pen into drawer

| Item | Value |
| :--- | :--- |
| Env origin | Table origin. The robot sits at the -x edge facing +x |
| Work point `WORK_POS` | (-0.231, 0, 0.994), on the top 0.15 m in from the -x edge. SO-101 base goes here |
| Pen | Work point + (0.20, -0.14), tip toward -y |
| Drawer | Work point + (0.30, 0.17), front faces the robot |
| SO-101 reach | ~0.45 m horizontal (measured) |
| `env_spacing` | 3.5 m (table is 2.44 m long) |
