# Isaac-Envs

Isaac Lab 에셋 저장소. 로봇·씬·소품의 USD 와 그걸 불러오는 cfg 만 둔다.
작업(보상·관측·종료 조건)은 여기서 만들지 않고, 이 패키지를 import 하는
SO-101 labs 에서 만든다.

```
isaac_envs/          cfg (pip install -e . 로 env_isaaclab 에 설치)
  robots/so101.py    SO101_CFG, SO101_HIGH_PD_CFG
  scenes/  props/    (예정)
assets/              실제 파일
  robots/so101/urdf  공식 SO-ARM100 원본 (SOURCE.txt 에 커밋·라이선스)
  robots/so101/usd   convert_urdf.py 로 만든 USD
scripts/
  convert_urdf.py    URDF -> USD, 변환 뒤 단위·관절·바디 검사
  preview.py         cfg 를 띄워 자세 유지·관절별 추종 검사
```

## 쓰는 법

```
conda activate env_isaaclab          # Isaac Sim 5.1 + Isaac Lab 2.3.2
pip install -e .

python scripts/convert_urdf.py assets/robots/so101/urdf/so101_new_calib.urdf \
    assets/robots/so101/usd so101.usd
python scripts/preview.py SO101_CFG --headless
```

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
- `preview.py` 2026-10-12 결과: 둘 다 STABLE. 자세 유지 오차 최대 1.38° / 0.45°.
  `shoulder_lift` +50° 는 바닥에 닿아 못 간다(`--no-ground` 면 1.6°).
