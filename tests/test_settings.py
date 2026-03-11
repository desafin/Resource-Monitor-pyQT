"""설정 저장/복원 기능에 대한 사양 테스트.

QSettings를 사용한 윈도우 크기, 테마, 업데이트 간격 저장/복원을 검증합니다.
"""
import sys
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from PyQt5.QtCore import QSettings


class TestSettingsPersistence:
    """설정 저장 및 복원 동작을 검증합니다."""

    @pytest.fixture(autouse=True)
    def clear_settings(self) -> None:
        """테스트 전후로 QSettings를 초기화합니다."""
        settings = QSettings("ResourceMonitor", "ResourceMonitor")
        settings.clear()
        yield
        settings = QSettings("ResourceMonitor", "ResourceMonitor")
        settings.clear()

    def test_save_window_size(self) -> None:
        """윈도우 크기를 저장하고 복원할 수 있어야 합니다."""
        from utils.settings_manager import save_window_size, load_window_size
        save_window_size(1024, 768)
        width, height = load_window_size()
        assert width == 1024
        assert height == 768

    def test_load_window_size_default(self) -> None:
        """저장된 설정이 없으면 기본 크기를 반환해야 합니다."""
        from utils.settings_manager import load_window_size
        width, height = load_window_size()
        assert width == 1280
        assert height == 800

    def test_save_theme(self) -> None:
        """테마 설정을 저장하고 복원할 수 있어야 합니다."""
        from utils.settings_manager import save_theme, load_theme
        save_theme(False)  # 라이트 테마
        assert load_theme() is False

    def test_load_theme_default(self) -> None:
        """저장된 설정이 없으면 기본 테마(다크)를 반환해야 합니다."""
        from utils.settings_manager import load_theme
        assert load_theme() is True

    def test_save_update_interval(self) -> None:
        """업데이트 간격을 저장하고 복원할 수 있어야 합니다."""
        from utils.settings_manager import save_update_interval, load_update_interval
        save_update_interval(5)
        assert load_update_interval() == 5

    def test_load_update_interval_default(self) -> None:
        """저장된 설정이 없으면 기본 간격(1초)을 반환해야 합니다."""
        from utils.settings_manager import load_update_interval
        assert load_update_interval() == 1

    def test_save_update_interval_clamped(self) -> None:
        """업데이트 간격이 범위(1-10)를 벗어나면 클램핑되어야 합니다."""
        from utils.settings_manager import save_update_interval, load_update_interval
        save_update_interval(0)
        assert load_update_interval() == 1
        save_update_interval(15)
        assert load_update_interval() == 10
