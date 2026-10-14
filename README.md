# Isaac-Envs

USD Storage

<br>

### Available Robots

| Img | Robot | Model Name |
| :---: | :--- | :--- |
| <img src="https://raw.githubusercontent.com/TheRobotStudio/SO-ARM100/a758567c3978dfeefe282ede0500085a48fe8f78/media/SO101_Follower.webp" width="120"> | SO-101 | `SO101_CFG`, `SO101_HIGH_PD_CFG` |
| <img src="https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1/Isaac/Robots/Ufactory/xarm7/.thumbs/256x256/xarm7.usd.png" width="120"> | UFACTORY xArm7 | `XARM7_CFG` |
| <img src="https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1/Isaac/Robots/Ufactory/xarm7/.thumbs/256x256/xarm7.usd.png" width="60"><img src="https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/6.0/Isaac/Robots/InspireRobots/Inspire_Hand_RH56DFX_right/.thumbs/256x256/inspire_hand.usda.png" width="60"> | xArm7 + Inspire RH56BFX | `XARM7_INSPIRE_RH56BFX_CFG` |
| <img src="https://raw.githubusercontent.com/unitreerobotics/unitree_ros/5994d4faef0a9cadd3287f8de0199a67eeb2a259/robots/g1_description/images/g1_29dof.png" width="120"> | Unitree G1 (29 DoF) | `G1_CFG` |
| <img src="https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/6.0/Isaac/Robots/InspireRobots/Inspire_Hand_RH56DFX_right/.thumbs/256x256/inspire_hand.usda.png" width="120"> | Inspire RH56BFX (right hand) | `INSPIRE_RH56BFX_CFG` |

### Envs & Objects

- [Envs.md](Envs.md): scenes
- [Objects.md](Objects.md): props (table, desk, pen, pan, drawer, cube, tray)

### Interface (`sims/`)

What [Interface](https://github.com/Chany-Lab/Interface) reads, by LeRobot type.

| Path | Content |
| :--- | :--- |
| `sims/robots/<type>/` | USDA referencing a robot under `assets/`, and `robot.yaml` (start pose, TCP link) |
| `sims/tools/<id>/` | Same for end effectors |
| `sims/envs/` | Shared environment scripts (`build(scene)`, e.g. `lift_cube.py`) |
| `assets/props/<name>/` | Props the sim server places by name |

| Interface id | Robot |
| :--- | :--- |
| `so101_follower` | SO-101 |
| `ufactory_xarm7` | xArm7 |
| `ufactory_xarm7_inspire_rh56bfx` | xArm7 + Inspire RH56BFX |
| `inspire_rh56bfx` (tool) | Inspire RH56BFX |

## Setup Guide

| Component | Version |
| :--- | :--- |
| Python | 3.12 |
| Isaac Sim | 6.2.0 (`isaacsim[all,extscache]`) |
| Isaac Lab | 3.0 (`release/3.0.0` @ `d061bf3`, from git) |
| Physics | PhysX (Newton 1.6.1 installed too) |
| torch | 2.11.0 (cu130), NVIDIA driver 580+ |

Managed with uv. `setup.sh` checks git-lfs, uv and the driver, pulls the
LFS assets and runs `uv sync`; run it again at any time.

```bash
./setup.sh            # --check: only verify, --no-sim: assets and dev tools only
export OMNI_KIT_ACCEPT_EULA=YES

uv run python scripts/preview.py SO101_CFG                          # view a robot
uv run python scripts/preview.py --scene PEN_INTO_DRAWER_SCENE_CFG  # view a scene
```

Other projects add this repo as a dependency and bring their own Isaac Lab
(3.0; quaternions are `(x, y, z, w)`). After changing prop dims or robot
gains, rerun `scripts/build_props.py` or `scripts/write_drive_gains.py`.
