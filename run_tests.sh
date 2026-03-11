#!/bin/bash
# ROS PYTHONPATH 충돌을 피하면서 pytest를 실행하는 헬퍼 스크립트
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLEAN_PATH=$(echo "$PYTHONPATH" | tr ':' '\n' | grep -v '/ros/' | tr '\n' ':')
PYTHONPATH="${SCRIPT_DIR}:${CLEAN_PATH}" python -m pytest "$@"
