"""views/network_viewmodel.py에 대한 사양 테스트.

NetworkViewModel(QObject)의 Q_PROPERTY, 속도 포맷팅 기능을 검증합니다.
"""
import pytest
from unittest.mock import patch, MagicMock

from PyQt5.QtCore import QObject

from views.network_viewmodel import NetworkViewModel


class TestNetworkViewModelInit:
    """NetworkViewModel 초기화를 검증합니다."""

    def test_creates_instance(self, qapp) -> None:
        """NetworkViewModel 인스턴스를 생성할 수 있어야 합니다."""
        vm = NetworkViewModel()
        assert vm is not None

    def test_is_qobject(self, qapp) -> None:
        """QObject를 상속해야 합니다."""
        vm = NetworkViewModel()
        assert isinstance(vm, QObject)

    def test_has_network_model_property(self, qapp) -> None:
        """networkModel 프로퍼티가 있어야 합니다."""
        vm = NetworkViewModel()
        model = vm.property("networkModel")
        assert model is not None


class TestNetworkViewModelNetworkModel:
    """NetworkViewModel.networkModel 프로퍼티를 검증합니다."""

    def test_network_model_is_network_model_instance(self, qapp) -> None:
        """networkModel은 NetworkModel 인스턴스여야 합니다."""
        from models.network_model import NetworkModel
        vm = NetworkViewModel()
        assert isinstance(vm.networkModel, NetworkModel)


class TestNetworkViewModelFormatSpeed:
    """NetworkViewModel의 속도 포맷팅 기능을 검증합니다."""

    def test_format_speed_zero(self, qapp) -> None:
        """0 B/s를 올바르게 포맷해야 합니다."""
        vm = NetworkViewModel()
        assert vm.formatSpeed(0) == "0 B/s"

    def test_format_speed_bytes(self, qapp) -> None:
        """바이트 단위 속도를 올바르게 포맷해야 합니다."""
        vm = NetworkViewModel()
        result = vm.formatSpeed(500)
        assert "B/s" in result

    def test_format_speed_kb(self, qapp) -> None:
        """킬로바이트 단위 속도를 올바르게 포맷해야 합니다."""
        vm = NetworkViewModel()
        result = vm.formatSpeed(1024)
        assert "KB/s" in result

    def test_format_speed_mb(self, qapp) -> None:
        """메가바이트 단위 속도를 올바르게 포맷해야 합니다."""
        vm = NetworkViewModel()
        result = vm.formatSpeed(1024 * 1024)
        assert "MB/s" in result

    def test_format_speed_gb(self, qapp) -> None:
        """기가바이트 단위 속도를 올바르게 포맷해야 합니다."""
        vm = NetworkViewModel()
        result = vm.formatSpeed(1024 ** 3)
        assert "GB/s" in result

    def test_format_speed_precise(self, qapp) -> None:
        """정확한 속도 값을 반환해야 합니다."""
        vm = NetworkViewModel()
        # 1.5 MB/s = 1572864 bytes/sec
        result = vm.formatSpeed(1_572_864)
        assert "1.5" in result
        assert "MB/s" in result


class TestNetworkViewModelFormatBytes:
    """NetworkViewModel의 바이트 포맷팅 기능을 검증합니다."""

    def test_format_bytes_zero(self, qapp) -> None:
        """0 바이트를 올바르게 포맷해야 합니다."""
        vm = NetworkViewModel()
        assert vm.formatBytes(0) == "0 B"

    def test_format_bytes_gb(self, qapp) -> None:
        """기가바이트 단위를 올바르게 포맷해야 합니다."""
        vm = NetworkViewModel()
        result = vm.formatBytes(1024 ** 3)
        assert "GB" in result


class TestNetworkViewModelPing:
    """NetworkViewModel의 ping 관련 기능을 검증합니다."""

    def test_has_ping_target_property(self, qapp) -> None:
        """pingTarget 프로퍼티가 있어야 합니다."""
        vm = NetworkViewModel()
        assert vm.property("pingTarget") is not None or vm.property("pingTarget") == ""

    def test_has_is_pinging_property(self, qapp) -> None:
        """isPinging 프로퍼티가 있어야 합니다."""
        vm = NetworkViewModel()
        # 초기값은 False
        assert vm.property("isPinging") is False

    def test_has_ping_result_property(self, qapp) -> None:
        """pingResult 프로퍼티가 있어야 합니다."""
        vm = NetworkViewModel()
        result = vm.property("pingResult")
        assert result is not None or result == ""

    def test_has_ping_error_property(self, qapp) -> None:
        """pingError 프로퍼티가 있어야 합니다."""
        vm = NetworkViewModel()
        error = vm.property("pingError")
        assert error is not None or error == ""

    def test_initial_ping_target_is_empty(self, qapp) -> None:
        """초기 pingTarget은 빈 문자열이어야 합니다."""
        vm = NetworkViewModel()
        assert vm.property("pingTarget") == ""

    def test_initial_is_pinging_is_false(self, qapp) -> None:
        """초기 isPinging은 False여야 합니다."""
        vm = NetworkViewModel()
        assert vm.property("isPinging") is False

    def test_has_execute_ping_slot(self, qapp) -> None:
        """executePing 슬롯이 있어야 합니다."""
        vm = NetworkViewModel()
        assert hasattr(vm, "executePing")

    def test_cleanup_method_exists(self, qapp) -> None:
        """cleanup 메서드가 있어야 합니다."""
        vm = NetworkViewModel()
        assert hasattr(vm, "cleanup")
        assert callable(vm.cleanup)


class TestNetworkViewModelTimerControl:
    """NetworkViewModel 타이머 제어를 검증합니다."""

    def test_start_timer_starts_timer(self, qapp) -> None:
        """startTimer()는 내부 타이머를 시작해야 합니다."""
        vm = NetworkViewModel()
        with patch.object(vm._monitor, "measure", return_value={}), \
             patch.object(vm._network_model, "update_interfaces"):
            vm.startTimer()
            assert vm._timer.isActive()
            vm.stopTimer()

    def test_stop_timer_stops_active_timer(self, qapp) -> None:
        """stopTimer()는 활성화된 타이머를 중지해야 합니다."""
        vm = NetworkViewModel()
        with patch.object(vm._monitor, "measure", return_value={}), \
             patch.object(vm._network_model, "update_interfaces"):
            vm.startTimer()
            vm.stopTimer()
            assert not vm._timer.isActive()

    def test_start_timer_calls_update_immediately(self, qapp) -> None:
        """startTimer()는 즉시 _update()를 호출하여 초기 데이터를 수집해야 합니다."""
        vm = NetworkViewModel()
        with patch.object(vm._monitor, "measure", return_value={}) as mock_measure, \
             patch.object(vm._network_model, "update_interfaces"):
            vm.startTimer()
            mock_measure.assert_called_once()
            vm.stopTimer()


class TestNetworkViewModelPingTarget:
    """NetworkViewModel.pingTarget 프로퍼티 setter를 검증합니다."""

    def test_set_ping_target_updates_value(self, qapp) -> None:
        """pingTarget setter가 값을 정상적으로 업데이트해야 합니다."""
        vm = NetworkViewModel()
        vm.pingTarget = "8.8.8.8"
        assert vm.pingTarget == "8.8.8.8"

    def test_set_same_ping_target_does_not_emit_signal(self, qapp) -> None:
        """동일한 값으로 설정 시 시그널을 발생시키지 않아야 합니다."""
        vm = NetworkViewModel()
        vm.pingTarget = "1.1.1.1"
        emitted = []
        vm.pingTargetChanged.connect(lambda: emitted.append(True))
        vm.pingTarget = "1.1.1.1"  # 동일한 값
        assert len(emitted) == 0

    def test_set_different_ping_target_emits_signal(self, qapp) -> None:
        """다른 값으로 설정 시 pingTargetChanged 시그널이 발생해야 합니다."""
        vm = NetworkViewModel()
        emitted = []
        vm.pingTargetChanged.connect(lambda: emitted.append(True))
        vm.pingTarget = "192.168.1.1"
        assert len(emitted) == 1


class TestNetworkViewModelExecutePing:
    """NetworkViewModel.executePing() 슬롯을 검증합니다."""

    def test_execute_ping_does_nothing_when_already_pinging(self, qapp) -> None:
        """이미 ping 중이면 executePing()이 추가 ping을 시작하지 않아야 합니다."""
        vm = NetworkViewModel()
        vm._is_pinging = True
        with patch.object(vm, "_ensure_ping_thread") as mock_ensure:
            vm.executePing("8.8.8.8")
            mock_ensure.assert_not_called()

    def test_execute_ping_clears_previous_results(self, qapp) -> None:
        """executePing() 호출 시 이전 ping 결과와 에러가 초기화되어야 합니다."""
        vm = NetworkViewModel()
        vm._ping_result = "이전 결과"
        vm._ping_error = "이전 에러"
        with patch.object(vm, "_ensure_ping_thread"), \
             patch.object(vm, "_ping_worker", create=True) as mock_worker:
            mock_worker.execute_ping = MagicMock()
            vm._ping_worker = mock_worker
            vm.executePing("8.8.8.8")
        assert vm._ping_result == ""
        assert vm._ping_error == ""


class TestNetworkViewModelPingCallbacks:
    """NetworkViewModel ping 콜백 메서드들을 검증합니다."""

    def test_on_ping_started_sets_is_pinging_true(self, qapp) -> None:
        """_on_ping_started()는 _is_pinging을 True로 설정해야 합니다."""
        vm = NetworkViewModel()
        vm._on_ping_started()
        assert vm._is_pinging is True

    def test_on_ping_finished_sets_is_pinging_false(self, qapp) -> None:
        """_on_ping_finished()는 _is_pinging을 False로 설정해야 합니다."""
        vm = NetworkViewModel()
        vm._is_pinging = True
        result = {
            "target": "8.8.8.8",
            "packets_transmitted": 4,
            "packets_received": 4,
            "packet_loss": 0.0,
            "rtt_min": 1.0,
            "rtt_avg": 2.0,
            "rtt_max": 3.0,
            "rtt_mdev": 0.5,
        }
        vm._on_ping_finished(result)
        assert vm._is_pinging is False

    def test_on_ping_finished_formats_result_string(self, qapp) -> None:
        """_on_ping_finished()는 ping 결과를 읽기 쉬운 문자열로 포맷해야 합니다."""
        vm = NetworkViewModel()
        result = {
            "target": "1.1.1.1",
            "packets_transmitted": 4,
            "packets_received": 4,
            "packet_loss": 0.0,
            "rtt_min": 5.0,
            "rtt_avg": 10.0,
            "rtt_max": 15.0,
            "rtt_mdev": 2.5,
        }
        vm._on_ping_finished(result)
        assert "1.1.1.1" in vm._ping_result
        assert "4" in vm._ping_result

    def test_on_ping_error_sets_is_pinging_false(self, qapp) -> None:
        """_on_ping_error()는 _is_pinging을 False로 설정해야 합니다."""
        vm = NetworkViewModel()
        vm._is_pinging = True
        vm._on_ping_error("타임아웃 오류")
        assert vm._is_pinging is False

    def test_on_ping_error_sets_ping_error_message(self, qapp) -> None:
        """_on_ping_error()는 에러 메시지를 _ping_error에 저장해야 합니다."""
        vm = NetworkViewModel()
        vm._on_ping_error("연결 거부됨")
        assert vm._ping_error == "연결 거부됨"


class TestNetworkViewModelEnsurePingThread:
    """NetworkViewModel._ensure_ping_thread() 메서드를 검증합니다."""

    def test_ensure_ping_thread_creates_thread_when_none(self, qapp) -> None:
        """_ping_thread가 None이면 새 QThread를 생성해야 합니다."""
        vm = NetworkViewModel()
        assert vm._ping_thread is None
        vm._ensure_ping_thread()
        assert vm._ping_thread is not None
        # 정리
        vm._ping_thread.quit()
        vm._ping_thread.wait(1000)

    def test_ensure_ping_thread_creates_worker_when_none(self, qapp) -> None:
        """_ping_thread가 None이면 PingWorker도 생성해야 합니다."""
        from services.ping_worker import PingWorker
        vm = NetworkViewModel()
        vm._ensure_ping_thread()
        assert vm._ping_worker is not None
        assert isinstance(vm._ping_worker, PingWorker)
        # 정리
        vm._ping_thread.quit()
        vm._ping_thread.wait(1000)

    def test_ensure_ping_thread_does_not_recreate_if_exists(self, qapp) -> None:
        """이미 스레드가 있으면 재생성하지 않아야 합니다."""
        vm = NetworkViewModel()
        vm._ensure_ping_thread()
        first_thread = vm._ping_thread
        vm._ensure_ping_thread()
        assert vm._ping_thread is first_thread
        # 정리
        vm._ping_thread.quit()
        vm._ping_thread.wait(1000)


class TestNetworkViewModelFormatBytesDecimal:
    """formatBytes() 소수점 포맷을 검증합니다."""

    def test_format_bytes_returns_decimal_for_non_integer_value(self, qapp) -> None:
        """소수 값은 소수점 한 자리로 포맷해야 합니다."""
        vm = NetworkViewModel()
        result = vm.formatBytes(1_572_864)  # 1.5 MB
        assert "1.5" in result
        assert "MB" in result

    def test_format_bytes_returns_integer_for_whole_value(self, qapp) -> None:
        """정수 값은 소수점 없이 포맷해야 합니다."""
        vm = NetworkViewModel()
        result = vm.formatBytes(1024)
        assert "1 KB" == result


class TestNetworkViewModelCleanup:
    """NetworkViewModel.cleanup() 메서드를 검증합니다."""

    def test_cleanup_without_ping_thread_does_not_raise(self, qapp) -> None:
        """ping 스레드 없이 cleanup()을 호출해도 예외가 발생하지 않아야 합니다."""
        vm = NetworkViewModel()
        vm._ping_thread = None
        vm.cleanup()  # 예외 없이 완료되어야 함

    def test_cleanup_stops_running_ping_thread(self, qapp) -> None:
        """실행 중인 ping 스레드가 있을 때 cleanup()은 스레드를 중지해야 합니다."""
        from PyQt5.QtCore import QThread
        vm = NetworkViewModel()
        mock_thread = MagicMock(spec=QThread)
        mock_thread.isRunning.return_value = True
        vm._ping_thread = mock_thread
        vm.cleanup()
        mock_thread.quit.assert_called_once()
        mock_thread.wait.assert_called_once_with(3000)
