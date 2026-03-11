"""디스크 사용량 모니터링 모듈.

psutil을 사용하여 디스크 파티션 정보 및 I/O 통계를 수집합니다.
"""
import logging
from typing import Any

import psutil

from monitor_base import ResourceMonitor

logger = logging.getLogger(__name__)


class DiskMonitor(ResourceMonitor):
    """디스크 파티션 사용량 및 I/O 통계를 모니터링합니다.

    psutil.disk_partitions()로 파티션 목록을 조회하고,
    각 파티션의 사용량과 전체 I/O 카운터를 수집합니다.
    """

    def __init__(self) -> None:
        super().__init__()
        self.current_measurement: list[dict[str, Any]] = []

    def measure(self) -> list[dict[str, Any]]:
        """디스크 파티션 정보와 I/O 통계를 측정합니다.

        Returns:
            파티션별 디스크 정보 딕셔너리 목록.
            각 딕셔너리에 device, mountpoint, fstype, total, used, free,
            percent, read_bytes, write_bytes 키가 포함됩니다.
        """
        disks: list[dict[str, Any]] = []

        # I/O 카운터 (전체 시스템)
        io = psutil.disk_io_counters()
        read_bytes = io.read_bytes if io else 0
        write_bytes = io.write_bytes if io else 0

        # 파티션별 사용량 수집
        partitions = psutil.disk_partitions()
        for part in partitions:
            try:
                usage = psutil.disk_usage(part.mountpoint)
            except PermissionError:
                logger.debug("디스크 접근 거부: %s", part.mountpoint)
                continue
            except OSError as e:
                logger.debug("디스크 조회 실패: %s (%s)", part.mountpoint, e)
                continue

            disks.append({
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent,
                "read_bytes": read_bytes,
                "write_bytes": write_bytes,
            })

        self.last_measurement = self.current_measurement
        self.current_measurement = disks
        return disks

    def get_measurement(self) -> list[dict[str, Any]]:
        """최신 디스크 측정값을 반환합니다."""
        return self.current_measurement
