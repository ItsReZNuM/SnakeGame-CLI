import pytest
from snakegame.terminal import TerminalDetector, TerminalInfo


def test_detect_termux():
    info = TerminalDetector.detect(env={"TERMUX_VERSION": "0.118.0"})
    assert info.is_termux is True
    assert "Termux" in info.name
    assert info.system == "android"
    assert info.recommended_fps == 20

    info_prefix = TerminalDetector.detect(env={"PREFIX": "/data/data/com.termux/files/usr"})
    assert info_prefix.is_termux is True


def test_detect_windows_terminal(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Windows")
    info = TerminalDetector.detect(env={"WT_SESSION": "test-guid"})
    assert info.is_windows_terminal is True
    assert info.name == "Windows Terminal"
    assert info.recommended_fps == 45
    assert info.supports_sync_update is True


def test_detect_classic_windows_conhost(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Windows")
    info = TerminalDetector.detect(env={})
    assert info.is_conhost is True
    assert info.name == "Classic CMD"
    assert info.recommended_fps == 20
    assert info.supports_sync_update is False


def test_detect_vscode(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Windows")
    info = TerminalDetector.detect(env={"TERM_PROGRAM": "vscode"})
    assert info.name == "VS Code Terminal"
    assert info.recommended_fps == 30
    assert info.supports_sync_update is True


def test_detect_macos_iterm(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    info = TerminalDetector.detect(env={"TERM_PROGRAM": "iTerm.app"})
    assert info.name == "iTerm2"
    assert info.system == "darwin"
    assert info.recommended_fps == 45
    assert info.supports_sync_update is True


def test_detect_macos_apple_terminal(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    info = TerminalDetector.detect(env={"TERM_PROGRAM": "Apple_Terminal"})
    assert info.name == "Apple Terminal"
    assert info.system == "darwin"


def test_detect_linux_kitty(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Linux")
    info = TerminalDetector.detect(env={"KITTY_WINDOW_ID": "1"})
    assert info.name == "Kitty"
    assert info.recommended_fps == 60
    assert info.supports_sync_update is True


def test_detect_linux_alacritty(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Linux")
    info = TerminalDetector.detect(env={"ALACRITTY_LOG": "/tmp/alacritty.log"})
    assert info.name == "Alacritty"
    assert info.recommended_fps == 60


def test_detect_tmux(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Linux")
    info = TerminalDetector.detect(env={"TMUX": "/tmp/tmux-1000/default"})
    assert info.name == "tmux"
    assert info.recommended_fps == 30


def test_default_detection_non_empty():
    info = TerminalDetector.detect()
    assert isinstance(info, TerminalInfo)
    assert len(info.name) > 0
    assert info.recommended_fps in (20, 30, 45, 60)
