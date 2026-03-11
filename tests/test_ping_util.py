"""utils/ping_util.py에 대한 사양 테스트.

validate_ping_target()과 run_ping() 함수를 검증합니다.
커맨드 인젝션 방지, 출력 파싱, 에러 처리를 확인합니다.
"""
import pytest
from unittest.mock import patch, MagicMock
import subprocess


class TestValidatePingTarget:
    """validate_ping_target() 함수를 검증합니다."""

    def test_valid_ipv4(self) -> None:
        """유효한 IPv4 주소는 True를 반환해야 합니다."""
        from utils.ping_util import validate_ping_target
        assert validate_ping_target("192.168.1.1") is True

    def test_valid_hostname(self) -> None:
        """유효한 호스트명은 True를 반환해야 합니다."""
        from utils.ping_util import validate_ping_target
        assert validate_ping_target("google.com") is True

    def test_valid_subdomain(self) -> None:
        """서브도메인이 포함된 호스트명은 True를 반환해야 합니다."""
        from utils.ping_util import validate_ping_target
        assert validate_ping_target("www.example.com") is True

    def test_valid_ipv6(self) -> None:
        """IPv6 주소(콜론 포함)는 True를 반환해야 합니다."""
        from utils.ping_util import validate_ping_target
        assert validate_ping_target("::1") is True

    def test_valid_hostname_with_dash(self) -> None:
        """대시가 포함된 호스트명은 True를 반환해야 합니다."""
        from utils.ping_util import validate_ping_target
        assert validate_ping_target("my-server.local") is True

    def test_rejects_empty_string(self) -> None:
        """빈 문자열은 False를 반환해야 합니다."""
        from utils.ping_util import validate_ping_target
        assert validate_ping_target("") is False

    def test_rejects_command_injection_semicolon(self) -> None:
        """세미콜론을 이용한 커맨드 인젝션을 차단해야 합니다."""
        from utils.ping_util import validate_ping_target
        assert validate_ping_target("8.8.8.8; rm -rf /") is False

    def test_rejects_command_injection_pipe(self) -> None:
        """파이프를 이용한 커맨드 인젝션을 차단해야 합니다."""
        from utils.ping_util import validate_ping_target
        assert validate_ping_target("8.8.8.8 | cat /etc/passwd") is False

    def test_rejects_command_injection_backtick(self) -> None:
        """백틱을 이용한 커맨드 인젝션을 차단해야 합니다."""
        from utils.ping_util import validate_ping_target
        assert validate_ping_target("`rm -rf /`") is False

    def test_rejects_command_injection_dollar(self) -> None:
        """$()를 이용한 커맨드 인젝션을 차단해야 합니다."""
        from utils.ping_util import validate_ping_target
        assert validate_ping_target("$(whoami)") is False

    def test_rejects_spaces(self) -> None:
        """공백이 포함된 입력은 False를 반환해야 합니다."""
        from utils.ping_util import validate_ping_target
        assert validate_ping_target("8.8.8.8 extra") is False

    def test_rejects_ampersand(self) -> None:
        """&를 이용한 커맨드 인젝션을 차단해야 합니다."""
        from utils.ping_util import validate_ping_target
        assert validate_ping_target("8.8.8.8 && echo pwned") is False


class TestRunPing:
    """run_ping() 함수를 검증합니다."""

    @patch("utils.ping_util.subprocess.run")
    def test_successful_ping(self, mock_run: MagicMock) -> None:
        """성공적인 ping 결과를 올바르게 파싱해야 합니다."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=(
                "PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.\n"
                "64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=5.12 ms\n"
                "64 bytes from 8.8.8.8: icmp_seq=2 ttl=117 time=4.98 ms\n"
                "64 bytes from 8.8.8.8: icmp_seq=3 ttl=117 time=5.30 ms\n"
                "64 bytes from 8.8.8.8: icmp_seq=4 ttl=117 time=5.05 ms\n"
                "\n"
                "--- 8.8.8.8 ping statistics ---\n"
                "4 packets transmitted, 4 received, 0% packet loss, time 3004ms\n"
                "rtt min/avg/max/mdev = 4.980/5.112/5.300/0.117 ms\n"
            ),
            stderr="",
        )

        from utils.ping_util import run_ping
        result = run_ping("8.8.8.8")

        assert result["target"] == "8.8.8.8"
        assert result["packets_transmitted"] == 4
        assert result["packets_received"] == 4
        assert result["packet_loss"] == pytest.approx(0.0)
        assert result["rtt_min"] == pytest.approx(4.980)
        assert result["rtt_avg"] == pytest.approx(5.112)
        assert result["rtt_max"] == pytest.approx(5.300)
        assert result["rtt_mdev"] == pytest.approx(0.117)

    @patch("utils.ping_util.subprocess.run")
    def test_host_unreachable(self, mock_run: MagicMock) -> None:
        """호스트에 도달할 수 없을 때 패킷 손실을 올바르게 파싱해야 합니다."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout=(
                "PING 192.168.99.99 (192.168.99.99) 56(84) bytes of data.\n"
                "\n"
                "--- 192.168.99.99 ping statistics ---\n"
                "4 packets transmitted, 0 received, 100% packet loss, time 3006ms\n"
            ),
            stderr="",
        )

        from utils.ping_util import run_ping
        result = run_ping("192.168.99.99")

        assert result["packets_transmitted"] == 4
        assert result["packets_received"] == 0
        assert result["packet_loss"] == pytest.approx(100.0)

    @patch("utils.ping_util.subprocess.run")
    def test_dns_failure(self, mock_run: MagicMock) -> None:
        """DNS 해석 실패 시 에러를 반환해야 합니다."""
        mock_run.return_value = MagicMock(
            returncode=2,
            stdout="",
            stderr="ping: nonexistent.invalid: Name or service not known\n",
        )

        from utils.ping_util import run_ping
        result = run_ping("nonexistent.invalid")

        assert "error" in result

    @patch("utils.ping_util.subprocess.run")
    def test_timeout(self, mock_run: MagicMock) -> None:
        """프로세스 타임아웃 시 에러를 반환해야 합니다."""
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd="ping", timeout=15
        )

        from utils.ping_util import run_ping
        result = run_ping("8.8.8.8")

        assert "error" in result

    def test_invalid_target_returns_error(self) -> None:
        """유효하지 않은 대상에 대해 에러를 반환해야 합니다."""
        from utils.ping_util import run_ping
        result = run_ping("; rm -rf /")

        assert "error" in result

    @patch("utils.ping_util.subprocess.run")
    def test_uses_shell_false(self, mock_run: MagicMock) -> None:
        """보안을 위해 shell=False로 실행해야 합니다."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=(
                "4 packets transmitted, 4 received, 0% packet loss, time 3004ms\n"
                "rtt min/avg/max/mdev = 1.0/2.0/3.0/0.5 ms\n"
            ),
            stderr="",
        )

        from utils.ping_util import run_ping
        run_ping("8.8.8.8")

        # subprocess.run 호출 인자 검증
        call_args = mock_run.call_args
        # shell 키워드가 없거나 False여야 함
        assert call_args.kwargs.get("shell", False) is False

    @patch("utils.ping_util.subprocess.run")
    def test_partial_packet_loss(self, mock_run: MagicMock) -> None:
        """부분적 패킷 손실을 올바르게 파싱해야 합니다."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=(
                "4 packets transmitted, 2 received, 50% packet loss, time 3004ms\n"
                "rtt min/avg/max/mdev = 1.0/2.0/3.0/0.5 ms\n"
            ),
            stderr="",
        )

        from utils.ping_util import run_ping
        result = run_ping("8.8.8.8")

        assert result["packets_transmitted"] == 4
        assert result["packets_received"] == 2
        assert result["packet_loss"] == pytest.approx(50.0)

    @patch("utils.ping_util.subprocess.run")
    def test_subprocess_exception(self, mock_run: MagicMock) -> None:
        """subprocess에서 일반 예외 발생 시 에러를 반환해야 합니다."""
        mock_run.side_effect = OSError("ping 명령을 찾을 수 없습니다")

        from utils.ping_util import run_ping
        result = run_ping("8.8.8.8")

        assert "error" in result
