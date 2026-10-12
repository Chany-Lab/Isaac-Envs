# Isaac-Envs

Isaac Lab 에셋 저장소. 로봇·씬·소품의 USD 와 그걸 불러오는 cfg 만 둔다.
작업(보상·관측·종료 조건)은 여기서 만들지 않고, 이 패키지를 import 하는
labs 에서 만든다.

```
isaac_envs/          cfg (uv sync 로 .venv 에 설치)
  robots/so101.py    SO101_CFG, SO101_HIGH_PD_CFG
  robots/g1.py       G1_CFG, Unitree G1 29 자유도, 자유 베이스 (RL 용)
  robots/xarm7.py    XARM7_CFG, UFACTORY xArm7, 그리퍼 없음
  robots/inspire_rh56bfx.py  INSPIRE_RH56BFX_CFG, Inspire 오른손 단독
  robots/xarm7_inspire_rh56bfx.py  XARM7_INSPIRE_RH56BFX_CFG, xArm7 + Inspire 손
  props/<소품>/       소품마다 폴더 하나: cfg.py 에 cfg, dims.py 에 치수
                     (dims.py 는 빌더와 cfg 가 같이 쓴다)
  props/table/       TABLE_CFG, 모든 씬이 같이 쓰는 Isaac Sim 패킹 테이블, 정적
  props/pan/         PAN_CFG, 강체 0.15 kg (부품별 질량), 손잡이 +x
  props/pen/         PEN_CFG, 볼펜 강체 12 g (부품별 질량), 육각 몸통, 촉 +x
  props/drawer/      DRAWER_CFG, 서랍 하나짜리 장. 관절 `slide`
                     0 닫힘 ~ 0.12 m 열림, 수동 감쇠, 앞면 +x. MDF 밀도로
                     판마다 질량 (장 0.85 kg, 서랍 0.45 kg)
  scenes/<씬>/       씬마다 폴더 하나, cfg.py 에 씬 cfg. 이름은 로봇이 아니라
                     하는 일로 짓는다 (로봇은 지금 SO-101 고정)
  scenes/pen_into_drawer/  PenIntoDrawerSceneCfg / PEN_INTO_DRAWER_SCENE_CFG
assets/              실제 파일
  robots/so101/urdf  공식 SO-ARM100 원본 (SOURCE.txt 에 커밋·라이선스)
  robots/so101/usd   convert_urdf.py 로 만든 USD
  robots/g1/urdf     unitree_ros g1_description 원본 (SOURCE.txt)
  robots/g1/usd      convert_urdf.py 로 만든 USD (자유 베이스, convex hull)
  robots/xarm7/usd   Mimic 에서 가져온 Isaac Sim 5.1 xArm7 USD (SOURCE.txt)
  robots/inspire_rh56bfx/usd  Mimic 에서 가져온 Isaac Sim 6.0 Inspire 손 USD
                     + Isaac Lab 용 래퍼 *_isaaclab.usda (SOURCE.txt)
  robots/xarm7_inspire_rh56bfx/usd  위 둘을 참조해 붙인 Mimic 합본 USDA
  props/table        Isaac Sim 패킹 테이블 원본 + 래퍼 table.usda (SOURCE.txt)
  props/{pan,pen,drawer}/*.usd  build_props.py 로 만든 USD
scripts/
  convert_urdf.py    URDF -> USD, 변환 뒤 단위·관절·바디 검사
  build_props.py     props/*/dims.py 치수로 소품 USD 생성
  preview.py         cfg 나 씬을 올려 초기 자세로 둔다 (명령 없음)
  write_drive_gains.py  로봇 cfg 의 게인을 USD 관절 드라이브에 쓴다
```

## 쓰는 법

Python 3.11 + Isaac Sim 5.1.0 + Isaac Lab 2.3.2 + torch 2.7.0 (cu128).
3.12 는 Isaac Lab 3.0 이 필요한데 아직 정식 릴리스가 없다.

```
uv sync                               # .venv, 처음엔 수 GB 받는다
export OMNI_KIT_ACCEPT_EULA=YES

uv run python scripts/convert_urdf.py assets/robots/so101/urdf/so101_new_calib.urdf \
    assets/robots/so101/usd so101.usd
uv run python scripts/preview.py SO101_CFG              # 뷰어
uv run python scripts/preview.py SO101_CFG --headless   # 불러오기만 확인
uv run python scripts/preview.py G1_CFG --fix-base     # 휴머노이드는 몸통을 고정해서 본다
uv run python scripts/convert_urdf.py assets/robots/g1/urdf/g1_29dof_rev_1_0.urdf \
    assets/robots/g1/usd g1_29dof.usd --floating-base --collider convex_hull

uv run python scripts/build_props.py                    # props/*/dims.py 고친 뒤 소품 USD 재생성
uv run python scripts/write_drive_gains.py              # 로봇 cfg 게인 고친 뒤, 또는 URDF 재변환 뒤
uv run python scripts/preview.py --scene PEN_INTO_DRAWER_SCENE_CFG   # 씬 보기
```

`preview.py` 는 아무 명령도 보내지 않는다. 로봇은 초기 자세만 유지한다.

다른 프로젝트(labs)는 이 저장소를 의존성으로 넣는다. `dependencies` 가 비어
있어서 Isaac Lab 버전은 labs 쪽 것을 쓴다.

```python
from isaac_envs.robots import SO101_CFG
robot = SO101_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
```

## SO-101

| cfg | 게인 | 용도 |
|---|---|---|
| `SO101_CFG` | 공식 STS3215 식별값 (kp 17.8, damping 0.6, armature 0.028, friction 0.052), 토크 1.91 N·m, 5.45 rad/s | 실물에 가까운 동작 |
| `SO101_HIGH_PD_CFG` | isaac_so_arm101 의 관절별 고게인 | 정확한 추종이 필요한 작업 |

- TCP 는 `gripper_frame_link` (변환 때 병합하지 않는다).
- 12 V STS3215 면 `effort_limit_sim` 을 2.94 로.
- 2026-10-12 물리 검증(관절별 추종 시험): 둘 다 안정. 자세 유지 오차 최대
  1.38° / 0.45°.

## 로봇 게인

게인의 기준은 `isaac_envs/robots/` 의 cfg 다. `write_drive_gains.py` 가 같은
값(강성·감쇠·토크·속도 한계·armature)을 각 USD 의 루트 레이어에 덮어써서, USD
만 열어도 (Isaac Sim, Mimic) 같은 게인이 된다. cfg 게인을 바꾸거나 URDF 를
다시 변환하면 이 스크립트를 다시 돌린다.

| 로봇 | 게인 출처 |
|---|---|
| SO-101 | 공식 STS3215 식별값 |
| G1 | Unitree unitree_rl_lab `UNITREE_G1_29DOF_CFG` |
| xArm7 | ManiSkill xArm7 (강성 1000, 감쇠 100), 토크 한계는 UFACTORY 사양 |
| Inspire 손 | Isaac Lab `G1_INSPIRE_FTP_CFG` 손 (강성 10, 감쇠 0.2) |

## G1

- unitree_ros `g1_29dof_rev_1_0.urdf` (손 없음, 29 관절, 허리 3 축).
- 액추에이터 그룹·한계·게인·초기 자세는 Unitree 의 Isaac Lab RL 저장소
  unitree_rl_lab 의 `UNITREE_G1_29DOF_CFG` 를 따른다 (모터 모델별 그룹).
- 실물 SDK 모터 순서는 `isaac_envs.robots.g1.G1_SDK_JOINTS`.
- 몸통을 고정하면 초기 자세를 유지한다 (최대 오차 4°, 허리 pitch). 풀면 정책
  없이는 넘어진다.

## xArm7 / Inspire 손

Mimic (`~/ws/Mimic/data/sims`) 의 USD 를 가져왔다. 게인은 위 표.

- xArm7: 베이스를 자기 `root_joint` 로 월드에 고정한다. 초기 자세는 Mimic 과
  같은 joint2 -47.5°, joint7 9.6°. 토크 한계 50 / 30 / 20 N·m (1-2 / 3-5 / 6-7).
  실제 컨트롤러처럼 중력을 보상한 상태로 쓰려고 팔의 중력을 끈다 (Isaac Lab
  Franka cfg 와 같은 방식). 자세 유지·10° 스텝 오차 0.00°.
- Inspire 오른손: 구동 관절 6 개 (엄지 2, 네 손가락 1 번째 마디). 나머지는
  PhysX mimic 관절로 따라간다. 원본을 감싼 `inspire_rh56bfx_isaaclab.usda` 가
  원본의 PhysicsScene 과 월드 FixedJoint 를 끄고, 엄지 2 번 관절 한계를
  30° 에서 17.9° 로 줄인다 (그 위로는 mimic 과 한계가 싸워 엄지가 돈다).
- xArm7 + Inspire 합본 (`XARM7_INSPIRE_RH56BFX_CFG`): Mimic 의 합본 USDA 를
  가져와 참조만 이 저장소의 xArm7 과 손 래퍼로 바꿨다. 손 바닥(`r_base_link`)을
  link7 에 FixedJoint 로 붙이고 손의 아티큘레이션 루트를 지운다. 게인·엄지
  수정은 두 USD 에서 그대로 따라온다. 관절 19 개 (팔 7, 손 구동 6, mimic 6).

## 공용 테이블

모든 씬이 Isaac Sim 의 헤비듀티 패킹 테이블을 쓴다. Isaac Lab 의 G1·GR1
휴머노이드 pick-and-place 작업이 쓰는 테이블에서 상자·크레이트만 뺀 것이다.
철제 프레임에 라미네이트 상판.

- 상판 0.762 (x, 깊이) x 2.44 m (y, 길이), 윗면 높이 0.994 m.
- 원점은 상판 가운데 아래 바닥. 원본은 cm 단위·길이 방향 x 라서 래퍼
  `table.usda` 가 m 로 줄이고 90° 돌린다.
- 충돌: 상판은 박스, 프레임은 메시 그대로 (정적 삼각형 메시). 테이블 밑이 비어
  있어 다리·무릎이 들어간다. 볼트는 충돌 없음.
- 질량 90 kg (같은 크기 철제 패킹 테이블 기준 추정). 정적이라 작업에서
  동적으로 바꿀 때만 쓰인다.

## pen_into_drawer 씬

- env 원점 = 테이블 원점. 로봇은 -x 가장자리에서 +x 를 본다.
- 작업점 `WORK_POS` = (-0.231, 0, 0.994): -x 가장자리에서 0.15 m 안쪽 윗면.
  소품은 여기서부터 놓는다. SO-101 은 이 점에 베이스를 올린다.
- 볼펜: 작업점에서 (+0.20, -0.14), 촉은 -y 쪽. 몸통을 가로질러 잡는다.
- 서랍장: 작업점에서 (+0.30, +0.17), 앞면이 로봇을 본다. 서랍은 로봇 쪽으로 열린다.
- SO-101 수평 도달 거리 약 0.45 m (실측).
- 로봇은 지금 SO-101 로 고정. 나중에 `robot` 필드만 바꿔 다른 로봇을 쓴다.
- 테이블이 2.44 m 라 `env_spacing` 은 3.5 m.

labs 는 씬 cfg 를 가져와 작업 항목만 더한다. env 수는
`.replace(num_envs=...)` 로 정한다.

```python
from isaac_envs.scenes import PEN_INTO_DRAWER_SCENE_CFG
scene = PEN_INTO_DRAWER_SCENE_CFG.replace(num_envs=64)
```
