"""설정 관리 유틸리티.

QSettings를 사용하여 윈도우 크기, 테마, 업데이트 간격 등의
애플리케이션 설정을 저장하고 복원합니다.
"""
import logging

from PyQt5.QtCore import QSettings

logger = logging.getLogger(__name__)

# QSettings 조직/앱 이름
_ORG_NAME = "ResourceMonitor"
_APP_NAME = "ResourceMonitor"

# 기본값
_DEFAULT_WIDTH = 1280
_DEFAULT_HEIGHT = 800
_DEFAULT_DARK_THEME = True
_DEFAULT_UPDATE_INTERVAL = 1
_MIN_UPDATE_INTERVAL = 1
_MAX_UPDATE_INTERVAL = 10


def _get_settings() -> QSettings:
    """QSettings 인스턴스를 반환합니다."""
    return QSettings(_ORG_NAME, _APP_NAME)


def save_window_size(width: int, height: int) -> None:
    """윈도우 크기를 저장합니다.

    Args:
        width: 윈도우 너비 (픽셀).
        height: 윈도우 높이 (픽셀).
    """
    settings = _get_settings()
    settings.setValue("window/width", width)
    settings.setValue("window/height", height)
    logger.debug("윈도우 크기 저장: %dx%d", width, height)


def load_window_size() -> tuple[int, int]:
    """저장된 윈도우 크기를 반환합니다.

    Returns:
        (너비, 높이) 튜플. 저장된 값이 없으면 기본값 (1280, 800) 반환.
    """
    settings = _get_settings()
    width = int(settings.value("window/width", _DEFAULT_WIDTH))
    height = int(settings.value("window/height", _DEFAULT_HEIGHT))
    return width, height


def save_theme(is_dark: bool) -> None:
    """테마 설정을 저장합니다.

    Args:
        is_dark: True이면 다크 테마, False이면 라이트 테마.
    """
    settings = _get_settings()
    settings.setValue("theme/isDark", is_dark)
    logger.debug("테마 저장: %s", "다크" if is_dark else "라이트")


def load_theme() -> bool:
    """저장된 테마 설정을 반환합니다.

    Returns:
        True이면 다크 테마, False이면 라이트 테마.
        저장된 값이 없으면 기본값 True(다크) 반환.
    """
    settings = _get_settings()
    value = settings.value("theme/isDark", _DEFAULT_DARK_THEME)
    # QSettings는 문자열로 반환할 수 있으므로 변환 처리
    if isinstance(value, str):
        return value.lower() == "true"
    return bool(value)


def save_update_interval(seconds: int) -> None:
    """업데이트 간격을 저장합니다.

    범위를 벗어나는 값은 클램핑됩니다.

    Args:
        seconds: 업데이트 간격 (1-10초).
    """
    clamped = max(_MIN_UPDATE_INTERVAL, min(_MAX_UPDATE_INTERVAL, seconds))
    settings = _get_settings()
    settings.setValue("update/interval", clamped)
    logger.debug("업데이트 간격 저장: %d초", clamped)


def load_update_interval() -> int:
    """저장된 업데이트 간격을 반환합니다.

    Returns:
        업데이트 간격(초). 저장된 값이 없으면 기본값 1 반환.
    """
    settings = _get_settings()
    value = int(settings.value("update/interval", _DEFAULT_UPDATE_INTERVAL))
    return max(_MIN_UPDATE_INTERVAL, min(_MAX_UPDATE_INTERVAL, value))
