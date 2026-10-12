# Isaac-Envs

Isaac Lab 에셋 저장소. 로봇·씬·소품의 USD 와 그걸 불러오는 cfg 만 둔다.
작업(보상·관측·종료 조건)은 여기서 만들지 않고, 이 패키지를 import 하는
SO-101 labs 에서 만든다.

```
isaac_envs/          cfg (uv sync 로 .venv 에 설치)
  robots/so101.py    SO101_CFG, SO101_HIGH_PD_CFG
  props/dims.py      소품 치수 (빌더와 cfg 가 같이 쓴다)
  props/table.py     TABLE_CFG, 정적
  props/pan.py       PAN_CFG, 강체 0.15 kg, 손잡이 +x
  props/drawer.py    DRAWER_CFG, 서랍 하나짜리 장. 관절 `slide`
                     0 닫힘 ~ 0.12 m 열림, 수동 감쇠, 앞면 +x
  scenes/so101_tabletop.py  SO101TabletopSceneCfg / SO101_TABLETOP_SCENE_CFG
assets/              실제 파일
  robots/so101/urdf  공식 SO-ARM100 원본 (SOURCE.txt 에 커밋·라이선스)
  robots/so101/usd   convert_urdf.py 로 만든 USD
  props/{table,pan,drawer}/*.usd  build_props.py 로 만든 USD
scripts/
  convert_urdf.py    URDF -> USD, 변환 뒤 단위·관절·바디 검사
  build_props.py     dims.py 치수로 소품 USD 생성
  preview.py         cfg 나 씬을 올려 초기 자세로 둔다 (명령 없음)
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

uv run python scripts/build_props.py                    # dims.py 고친 뒤 소품 USD 재생성
uv run python scripts/preview.py --scene SO101_TABLETOP_SCENE_CFG   # 씬 보기
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

## SO101 tabletop 씬

- 로봇 베이스는 env 원점의 테이블 윗면 위, +x 를 본다.
- 테이블: 윗면 높이 0.40 m, 0.80 x 0.70 m, 로봇 뒤로 0.15 m 나온다.
- 팬: (0.20, -0.14), 손잡이는 -y 쪽.
- 서랍장: (0.30, +0.17), 앞면이 로봇을 본다. 서랍은 로봇 쪽으로 열린다.
- SO-101 수평 도달 거리 약 0.45 m (실측).

labs 는 씬 cfg 를 가져와 작업 항목만 더한다. env 수는
`.replace(num_envs=...)` 로 정한다.

```python
from isaac_envs.scenes import SO101_TABLETOP_SCENE_CFG
scene = SO101_TABLETOP_SCENE_CFG.replace(num_envs=64)
```
