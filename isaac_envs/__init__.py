"""Isaac Lab assets for the SO-101 labs: robots, scenes and props.

Only asset files and the cfgs that load them live here. Tasks (rewards,
observations, terminations) belong to the labs that import this package.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ASSETS_ROOT = REPO_ROOT / "assets"
