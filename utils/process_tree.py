"""프로세스 트리 구성 유틸리티.

평탄한 프로세스 목록을 ppid 관계를 기반으로 트리 구조로 변환합니다.
각 프로세스에 indent_level 키를 추가하여 계층 깊이를 나타냅니다.
"""
import logging
from collections import defaultdict
from typing import Optional

logger = logging.getLogger(__name__)


def build_process_tree(processes: list[dict]) -> list[dict]:
    """평탄한 프로세스 목록을 트리 순서로 재배열합니다.

    ppid 관계를 기반으로 부모-자식 트리를 구성하고,
    깊이 우선 순회(DFS) 순서로 프로세스를 정렬합니다.
    각 프로세스에 indent_level 키가 추가됩니다.

    Args:
        processes: ppid 키를 포함한 프로세스 딕셔너리 목록.

    Returns:
        indent_level 키가 추가된 트리 순서의 프로세스 목록.
    """
    if not processes:
        return []

    # pid -> 프로세스 매핑
    pid_map: dict[int, dict] = {}
    for proc in processes:
        pid_map[proc["pid"]] = proc

    # ppid -> 자식 프로세스 목록 매핑
    children: dict[int, list[dict]] = defaultdict(list)
    roots: list[dict] = []

    for proc in processes:
        ppid = proc.get("ppid", 0)
        if ppid in pid_map and ppid != proc["pid"]:
            children[ppid].append(proc)
        else:
            # 부모가 목록에 없거나 자기 자신이 부모인 경우 루트로 취급
            roots.append(proc)

    # 깊이 우선 순회로 트리 순서 생성
    result: list[dict] = []

    def _dfs(node: dict, level: int) -> None:
        """깊이 우선 순회로 프로세스를 트리 순서로 추가합니다."""
        node_copy = dict(node)
        node_copy["indent_level"] = level
        result.append(node_copy)
        # 자식을 PID 순으로 정렬하여 안정적인 순서 보장
        for child in sorted(children.get(node["pid"], []), key=lambda p: p["pid"]):
            _dfs(child, level + 1)

    # 루트 프로세스부터 시작 (PID 순)
    for root in sorted(roots, key=lambda p: p["pid"]):
        _dfs(root, 0)

    return result
