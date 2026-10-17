#!/usr/bin/env bash
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
target="${1:?用法: ./install.sh <题目目录> [v1|v2]}"
schema="${2:-v1}"
python3 "$here/install.py" --schema "$schema" --target "$target"
