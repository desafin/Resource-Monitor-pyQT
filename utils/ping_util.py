"""Ping 유틸리티 모듈.

지정된 대상에 ping을 실행하고 결과를 파싱합니다.
커맨드 인젝션을 방지하기 위해 입력 검증과 shell=False를 사용합니다.
"""
import logging
import re
import subprocess
from typing import Any, Dict

logger = logging.getLogger(__name__)

# 허용 문자: 영숫자, '.', '-', ':'(IPv6)
_VALID_TARGET_PATTERN = re.compile(r"^[a-zA-Z0-9.\-:]+$")

# ping 출력 파싱용 정규표현식
_PACKET_PATTERN = re.compile(
    r"(\d+) packets transmitted, (\d+) received.*?(\d+(?:\.\d+)?)% packet loss"
)
_RTT_PATTERN = re.compile(
    r"rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)"
)


def validate_ping_target(target: str) -> bool:
    """ping 대상 문자열을 검증합니다.

    커맨드 인젝션을 방지하기 위해 허용된 문자만 통과시킵니다.
    허용 문자: 영숫자, '.', '-', ':'

    Args:
        target: 검증할 대상 문자열.

    Returns:
        유효하면 True, 그렇지 않으면 False.
    """
    if not target:
        return False
    return bool(_VALID_TARGET_PATTERN.match(target))


def run_ping(target: str) -> Dict[str, Any]:
    """지정된 대상에 ping을 실행하고 결과를 반환합니다.

    4개의 ICMP 패킷을 전송하며 3초 대기, 전체 타임아웃 15초입니다.
    보안을 위해 항상 shell=False로 실행합니다.

    Args:
        target: ping 대상 호스트명 또는 IP 주소.

    Returns:
        성공 시: target, packets_transmitted, packets_received,
                packet_loss, rtt_min, rtt_avg, rtt_max, rtt_mdev를 포함하는 딕셔너리.
        실패 시: "error" 키를 포함하는 딕셔너리.
    """
    # 입력 검증
    if not validate_ping_target(target):
        return {"error": f"유효하지 않은 대상: {target}"}

    try:
        proc = subprocess.run(
            ["ping", "-c", "4", "-W", "3", target],
            capture_output=True,
            text=True,
            timeout=15,
        )

        output = proc.stdout

        # 출력이 없고 stderr에 에러가 있는 경우
        if not output and proc.stderr:
            return {"error": proc.stderr.strip()}

        # 패킷 통계 파싱
        packet_match = _PACKET_PATTERN.search(output)
        if not packet_match:
            # 파싱 실패 시 stderr 포함
            error_msg = proc.stderr.strip() if proc.stderr else "ping 출력을 파싱할 수 없습니다"
            return {"error": error_msg}

        result: Dict[str, Any] = {
            "target": target,
            "packets_transmitted": int(packet_match.group(1)),
            "packets_received": int(packet_match.group(2)),
            "packet_loss": float(packet_match.group(3)),
        }

        # RTT 통계 파싱 (패킷 수신이 있는 경우에만)
        rtt_match = _RTT_PATTERN.search(output)
        if rtt_match:
            result["rtt_min"] = float(rtt_match.group(1))
            result["rtt_avg"] = float(rtt_match.group(2))
            result["rtt_max"] = float(rtt_match.group(3))
            result["rtt_mdev"] = float(rtt_match.group(4))
        else:
            result["rtt_min"] = 0.0
            result["rtt_avg"] = 0.0
            result["rtt_max"] = 0.0
            result["rtt_mdev"] = 0.0

        return result

    except subprocess.TimeoutExpired:
        logger.warning("ping 타임아웃: %s", target)
        return {"error": f"ping 타임아웃 (15초 초과): {target}"}
    except Exception as e:
        logger.error("ping 실행 중 오류: %s", e)
        return {"error": str(e)}
