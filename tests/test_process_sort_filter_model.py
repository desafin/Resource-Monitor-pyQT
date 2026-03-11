"""models/process_sort_filter_model.py에 대한 사양 테스트.

ProcessSortFilterModel(QSortFilterProxyModel)의 필터링, 정렬, 프로퍼티를 검증합니다.
"""
import pytest
from PyQt5.QtCore import Qt

from models.process_model import ProcessModel
from models.process_sort_filter_model import ProcessSortFilterModel


@pytest.fixture
def model_with_data(qapp, sample_process_data) -> tuple[ProcessModel, ProcessSortFilterModel]:
    """소스 모델과 프록시 모델을 데이터와 함께 반환합니다."""
    source = ProcessModel()
    source.update_processes(sample_process_data)
    proxy = ProcessSortFilterModel()
    proxy.setSourceModel(source)
    return source, proxy


class TestProcessSortFilterModelInit:
    """ProcessSortFilterModel 초기화를 검증합니다."""

    def test_creates_instance(self, qapp) -> None:
        """인스턴스를 생성할 수 있어야 합니다."""
        proxy = ProcessSortFilterModel()
        assert proxy is not None

    def test_initial_search_text_empty(self, qapp) -> None:
        """초기 searchText는 빈 문자열이어야 합니다."""
        proxy = ProcessSortFilterModel()
        assert proxy.searchText == ""

    def test_initial_sort_column_is_cpu(self, qapp) -> None:
        """초기 sortColumn은 'cpu'여야 합니다."""
        proxy = ProcessSortFilterModel()
        assert proxy.sortColumn == "cpu"

    def test_initial_sort_order_descending(self, qapp) -> None:
        """초기 sortOrder는 Qt.DescendingOrder여야 합니다."""
        proxy = ProcessSortFilterModel()
        assert proxy.sortOrder == Qt.DescendingOrder


class TestProcessSortFilterModelFiltering:
    """ProcessSortFilterModel의 필터링을 검증합니다."""

    def test_no_filter_shows_all(self, model_with_data, sample_process_data) -> None:
        """필터 없이 모든 행이 표시되어야 합니다."""
        _, proxy = model_with_data
        assert proxy.rowCount() == len(sample_process_data)

    def test_filter_by_name(self, model_with_data) -> None:
        """이름으로 필터링하면 일치하는 프로세스만 표시되어야 합니다."""
        _, proxy = model_with_data
        proxy.searchText = "python"
        assert proxy.rowCount() == 1

    def test_filter_case_insensitive(self, model_with_data) -> None:
        """필터링은 대소문자를 구분하지 않아야 합니다."""
        _, proxy = model_with_data
        proxy.searchText = "PYTHON"
        assert proxy.rowCount() == 1

    def test_filter_by_partial_name(self, model_with_data) -> None:
        """부분 이름으로 필터링이 동작해야 합니다."""
        _, proxy = model_with_data
        proxy.searchText = "fire"
        assert proxy.rowCount() == 1

    def test_filter_no_match(self, model_with_data) -> None:
        """일치하는 프로세스가 없으면 0행이어야 합니다."""
        _, proxy = model_with_data
        proxy.searchText = "nonexistent_process_xyz"
        assert proxy.rowCount() == 0

    def test_clear_filter_restores_all(self, model_with_data, sample_process_data) -> None:
        """필터를 지우면 모든 행이 다시 표시되어야 합니다."""
        _, proxy = model_with_data
        proxy.searchText = "python"
        assert proxy.rowCount() == 1
        proxy.searchText = ""
        assert proxy.rowCount() == len(sample_process_data)


class TestProcessSortFilterModelSorting:
    """ProcessSortFilterModel의 정렬을 검증합니다."""

    def test_sort_by_cpu_descending(self, model_with_data) -> None:
        """CPU 내림차순 정렬 시 가장 높은 CPU 사용률이 첫 번째여야 합니다."""
        _, proxy = model_with_data
        proxy.sortColumn = "cpu"
        proxy.sortOrder = Qt.DescendingOrder

        # 첫 번째 행의 CPU 값이 두 번째보다 크거나 같아야 함
        first_cpu = proxy.data(proxy.index(0, 0), ProcessModel.CpuRole)
        second_cpu = proxy.data(proxy.index(1, 0), ProcessModel.CpuRole)
        assert first_cpu >= second_cpu

    def test_sort_by_name_ascending(self, model_with_data) -> None:
        """이름 오름차순 정렬이 동작해야 합니다."""
        _, proxy = model_with_data
        proxy.sortColumn = "name"
        proxy.sortOrder = Qt.AscendingOrder

        first_name = proxy.data(proxy.index(0, 0), ProcessModel.NameRole)
        second_name = proxy.data(proxy.index(1, 0), ProcessModel.NameRole)
        assert first_name.lower() <= second_name.lower()

    def test_sort_by_memory(self, model_with_data) -> None:
        """메모리 내림차순 정렬이 동작해야 합니다."""
        _, proxy = model_with_data
        proxy.sortColumn = "memory"
        proxy.sortOrder = Qt.DescendingOrder

        first_mem = proxy.data(proxy.index(0, 0), ProcessModel.MemRole)
        second_mem = proxy.data(proxy.index(1, 0), ProcessModel.MemRole)
        assert first_mem >= second_mem

    def test_sort_by_pid(self, model_with_data) -> None:
        """PID 오름차순 정렬이 동작해야 합니다."""
        _, proxy = model_with_data
        proxy.sortColumn = "pid"
        proxy.sortOrder = Qt.AscendingOrder

        first_pid = proxy.data(proxy.index(0, 0), ProcessModel.PidRole)
        second_pid = proxy.data(proxy.index(1, 0), ProcessModel.PidRole)
        assert first_pid <= second_pid


class TestProcessSortFilterModelProperties:
    """ProcessSortFilterModel의 Q_PROPERTY 설정을 검증합니다."""

    def test_set_search_text(self, qapp) -> None:
        """searchText 프로퍼티를 설정할 수 있어야 합니다."""
        proxy = ProcessSortFilterModel()
        proxy.searchText = "test"
        assert proxy.searchText == "test"

    def test_set_sort_column(self, qapp) -> None:
        """sortColumn 프로퍼티를 설정할 수 있어야 합니다."""
        proxy = ProcessSortFilterModel()
        proxy.sortColumn = "name"
        assert proxy.sortColumn == "name"

    def test_set_sort_order(self, qapp) -> None:
        """sortOrder 프로퍼티를 설정할 수 있어야 합니다."""
        proxy = ProcessSortFilterModel()
        proxy.sortOrder = Qt.AscendingOrder
        assert proxy.sortOrder == Qt.AscendingOrder
