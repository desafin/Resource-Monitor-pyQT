"""프로세스 목록의 검색 필터링 및 정렬을 위한 프록시 모델.

QSortFilterProxyModel을 상속하여 텍스트 검색 필터링과
컬럼별 정렬 기능을 제공합니다.
"""
import logging
from typing import Any, Optional

from PyQt5.QtCore import (
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
    pyqtProperty,
    pyqtSignal,
    pyqtSlot,
)

from models.process_model import ProcessModel

logger = logging.getLogger(__name__)

# 정렬 컬럼 이름과 역할 매핑
_SORT_COLUMN_MAP: dict[str, int] = {
    "pid": ProcessModel.PidRole,
    "name": ProcessModel.NameRole,
    "cpu": ProcessModel.CpuRole,
    "memory": ProcessModel.MemRole,
    "status": ProcessModel.StatusRole,
    "user": ProcessModel.UserRole,
    "threads": ProcessModel.ThreadsRole,
}


class ProcessSortFilterModel(QSortFilterProxyModel):
    """프로세스 목록의 텍스트 필터링과 컬럼별 정렬을 제공하는 프록시 모델.

    QML에서 searchText, sortColumn, sortOrder 프로퍼티로 제어합니다.
    """

    # 프로퍼티 변경 시그널
    searchTextChanged = pyqtSignal()
    sortColumnChanged = pyqtSignal()
    sortOrderChanged = pyqtSignal()

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        self._search_text: str = ""
        self._sort_column: str = "cpu"
        self._sort_order: int = Qt.DescendingOrder

        # 기본 정렬 설정 적용
        self.setDynamicSortFilter(True)
        self.setSortRole(ProcessModel.CpuRole)
        self.sort(0, Qt.DescendingOrder)

    # --- 검색 텍스트 프로퍼티 ---

    @pyqtProperty(str, notify=searchTextChanged)
    def searchText(self) -> str:
        """현재 검색 텍스트를 반환합니다."""
        return self._search_text

    @searchText.setter  # type: ignore[attr-defined]
    def searchText(self, text: str) -> None:
        """검색 텍스트를 설정하고 필터를 갱신합니다."""
        if self._search_text != text:
            self._search_text = text
            self.searchTextChanged.emit()
            self.invalidateFilter()

    # --- 정렬 컬럼 프로퍼티 ---

    @pyqtProperty(str, notify=sortColumnChanged)
    def sortColumn(self) -> str:
        """현재 정렬 컬럼 이름을 반환합니다."""
        return self._sort_column

    @sortColumn.setter  # type: ignore[attr-defined]
    def sortColumn(self, column: str) -> None:
        """정렬 컬럼을 설정하고 정렬을 갱신합니다."""
        if self._sort_column != column:
            self._sort_column = column
            role = _SORT_COLUMN_MAP.get(column, ProcessModel.CpuRole)
            self.setSortRole(role)
            self.sortColumnChanged.emit()
            self.sort(0, self._sort_order)

    # --- 정렬 순서 프로퍼티 ---

    @pyqtProperty(int, notify=sortOrderChanged)
    def sortOrder(self) -> int:
        """현재 정렬 순서를 반환합니다 (Qt.AscendingOrder 또는 Qt.DescendingOrder)."""
        return self._sort_order

    @sortOrder.setter  # type: ignore[attr-defined]
    def sortOrder(self, order: int) -> None:
        """정렬 순서를 설정하고 정렬을 갱신합니다."""
        if self._sort_order != order:
            self._sort_order = order
            self.sortOrderChanged.emit()
            self.sort(0, self._sort_order)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """검색 텍스트와 일치하는 행만 표시합니다.

        프로세스 이름과 사용자 이름을 대소문자 무시하고 비교합니다.
        """
        if not self._search_text:
            return True

        source_model = self.sourceModel()
        if source_model is None:
            return True

        index = source_model.index(source_row, 0, source_parent)
        search_lower = self._search_text.lower()

        # 이름과 사용자 이름에서 검색
        name = source_model.data(index, ProcessModel.NameRole)
        username = source_model.data(index, ProcessModel.UserRole)

        if name and search_lower in str(name).lower():
            return True
        if username and search_lower in str(username).lower():
            return True

        return False

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        """정렬 비교 함수. 현재 정렬 역할에 따라 비교합니다."""
        role = self.sortRole()
        left_data = self.sourceModel().data(left, role)
        right_data = self.sourceModel().data(right, role)

        # None 처리
        if left_data is None:
            return True
        if right_data is None:
            return False

        # 문자열은 대소문자 무시 비교
        if isinstance(left_data, str) and isinstance(right_data, str):
            return left_data.lower() < right_data.lower()

        return left_data < right_data
