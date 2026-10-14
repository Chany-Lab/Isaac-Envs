#!/usr/bin/env bash
# Set up Isaac-Envs: Git LFS assets and the uv environment (Python 3.12,
# Isaac Sim 6.2, Isaac Lab 3.0, torch cu130). Safe to run again.
#
#   ./setup.sh            check, pull LFS assets, install everything
#   ./setup.sh --check    only check the prerequisites and the current state
#   ./setup.sh --no-sim   assets and dev tools only, no Isaac Sim / Isaac Lab
#                         (enough for the USD files under assets/ and sims/)
set -euo pipefail

MIN_DRIVER=580 # CUDA 13 (torch cu130) needs driver 580 or newer
PYTHON=3.12

check_only=0
sim=1
for arg in "$@"; do
    case "$arg" in
        --check) check_only=1 ;;
        --no-sim) sim=0 ;;
        -h | --help)
            sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *)
            echo "unknown option: $arg (try --help)" >&2
            exit 2
            ;;
    esac
done

cd "$(dirname "${BASH_SOURCE[0]}")"

failed=0
ok() { printf '  ok    %s\n' "$*"; }
warn() { printf '  warn  %s\n' "$*"; }
fail() {
    printf '  FAIL  %s\n' "$*"
    failed=1
}

echo "Prerequisites"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    ok "git repository"
else
    fail "not a git checkout: clone the repo with git, the assets are in Git LFS"
fi

if git lfs version >/dev/null 2>&1; then
    ok "$(git lfs version | cut -d' ' -f1)"
else
    fail "git-lfs missing: sudo apt install git-lfs (or https://git-lfs.com)"
fi

if command -v uv >/dev/null 2>&1; then
    ok "$(uv --version)"
else
    fail "uv missing: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

if command -v uv >/dev/null 2>&1; then
    if py=$(uv python find "$PYTHON" 2>/dev/null); then
        ok "Python $PYTHON at $py"
    else
        ok "Python $PYTHON not installed; uv downloads it on sync"
    fi
fi

if [ "$sim" = 1 ]; then
    if command -v nvidia-smi >/dev/null 2>&1 &&
        driver=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -n1) &&
        [ -n "$driver" ]; then
        gpu=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -n1)
        if [ "${driver%%.*}" -ge "$MIN_DRIVER" ]; then
            ok "NVIDIA driver $driver ($gpu)"
        else
            fail "NVIDIA driver $driver is older than $MIN_DRIVER, which CUDA 13 needs"
        fi
    else
        fail "no NVIDIA driver (nvidia-smi not working); use --no-sim to skip Isaac Sim"
    fi
fi

if [ -n "${PYTHONPATH:-}" ]; then
    warn "PYTHONPATH is set (e.g. by ROS); Isaac Sim may pick up the wrong packages."
    warn "Run with 'env -u PYTHONPATH uv run ...' if imports fail."
fi

echo "State"

lfs_pointers=0
if git lfs version >/dev/null 2>&1; then
    # Files still stored as LFS pointers, i.e. not downloaded yet.
    lfs_pointers=$(git lfs ls-files 2>/dev/null | grep -c ' - ' || true)
    if [ "$lfs_pointers" = 0 ]; then
        ok "LFS assets downloaded"
    else
        warn "$lfs_pointers LFS files not downloaded yet"
    fi
fi

if [ -x .venv/bin/python ]; then
    ok ".venv ($(.venv/bin/python --version))"
else
    warn ".venv not created yet"
fi

if [ "$failed" = 1 ]; then
    echo "Fix the failures above, then run ./setup.sh again." >&2
    exit 1
fi

groups=()
[ "$sim" = 1 ] || groups=(--no-group sim)

if [ "$check_only" = 1 ]; then
    if uv sync --locked --check "${groups[@]}" >/dev/null 2>&1; then
        ok "environment matches uv.lock"
    else
        warn "environment out of date: run ./setup.sh${groups[*]:+ --no-sim}"
    fi
    exit 0
fi

echo "Setup"

git lfs install --local >/dev/null
git lfs pull
ok "LFS assets"

# The first sync downloads Isaac Sim (tens of GB); later runs only check.
uv sync --locked "${groups[@]}"
ok "uv environment"

if [ "$sim" = 0 ]; then
    echo
    echo "Done (no Isaac Sim). Run ./setup.sh without --no-sim to preview assets."
    exit 0
fi

cat <<'EOF'

Done. Isaac Sim asks for its EULA on first start; accept it once per shell:

    export OMNI_KIT_ACCEPT_EULA=YES

Then preview a robot or a scene:

    uv run python scripts/preview.py SO101_CFG
    uv run python scripts/preview.py --scene PEN_INTO_DRAWER_SCENE_CFG --headless
EOF
