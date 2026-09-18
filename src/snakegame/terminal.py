import os
import platform
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class TerminalInfo:
    name: str
    system: str
    is_termux: bool = False
    is_windows_terminal: bool = False
    is_conhost: bool = False
    recommended_fps: int = 30
    supports_sync_update: bool = False


class TerminalDetector:
    """Intelligently detects the running terminal environment and capabilities across platforms."""

    @staticmethod
    def detect(env: Optional[dict[str, str]] = None, system: Optional[str] = None) -> TerminalInfo:
        e = os.environ if env is None else env
        sys_name = (system if system is not None else platform.system()).lower()

        # 1. Android Termux
        if "TERMUX_VERSION" in e or "com.termux" in e.get("PREFIX", "") or "TERMUX_APP_PID" in e:
            return TerminalInfo(
                name="Termux (Android)",
                system="android",
                is_termux=True,
                recommended_fps=20,
                supports_sync_update=False,
            )

        # 2. Windows Environments
        if sys_name == "windows":
            if "WT_SESSION" in e:
                return TerminalInfo(
                    name="Windows Terminal",
                    system="windows",
                    is_windows_terminal=True,
                    recommended_fps=45,
                    supports_sync_update=True,
                )
            if "ConEmuPID" in e or "ConEmuBuild" in e:
                return TerminalInfo(
                    name="ConEmu / Cmder",
                    system="windows",
                    recommended_fps=30,
                    supports_sync_update=False,
                )
            if e.get("TERM_PROGRAM") == "vscode":
                return TerminalInfo(
                    name="VS Code Terminal",
                    system="windows",
                    recommended_fps=30,
                    supports_sync_update=True,
                )
            # Classic Windows Console (conhost.exe)
            return TerminalInfo(
                name="Classic CMD",
                system="windows",
                is_conhost=True,
                recommended_fps=20,
                supports_sync_update=False,
            )

        # 3. macOS Environments
        if sys_name == "darwin":
            term_prog = e.get("TERM_PROGRAM", "")
            if term_prog == "iTerm.app":
                return TerminalInfo(
                    name="iTerm2",
                    system="darwin",
                    recommended_fps=45,
                    supports_sync_update=True,
                )
            if term_prog == "Apple_Terminal":
                return TerminalInfo(
                    name="Apple Terminal",
                    system="darwin",
                    recommended_fps=30,
                    supports_sync_update=False,
                )
            if term_prog == "vscode":
                return TerminalInfo(
                    name="VS Code Terminal",
                    system="darwin",
                    recommended_fps=30,
                    supports_sync_update=True,
                )

        # 4. Linux / Modern POSIX Terminals
        if "KITTY_WINDOW_ID" in e:
            return TerminalInfo(
                name="Kitty",
                system=sys_name,
                recommended_fps=60,
                supports_sync_update=True,
            )
        if "ALACRITTY_LOG" in e or e.get("TERM") == "alacritty":
            return TerminalInfo(
                name="Alacritty",
                system=sys_name,
                recommended_fps=60,
                supports_sync_update=True,
            )
        if "WEZTERM_PANE" in e:
            return TerminalInfo(
                name="WezTerm",
                system=sys_name,
                recommended_fps=60,
                supports_sync_update=True,
            )
        if "TMUX" in e:
            return TerminalInfo(
                name="tmux",
                system=sys_name,
                recommended_fps=30,
                supports_sync_update=False,
            )
        if e.get("TERM_PROGRAM") == "vscode":
            return TerminalInfo(
                name="VS Code Terminal",
                system=sys_name,
                recommended_fps=30,
                supports_sync_update=True,
            )

        # Generic Fallback
        if sys_name == "darwin":
            fallback_name = "macOS Terminal"
        elif sys_name == "linux":
            fallback_name = "Linux Terminal"
        else:
            fallback_name = "Standard Terminal"

        return TerminalInfo(
            name=fallback_name,
            system=sys_name,
            recommended_fps=30,
            supports_sync_update=False,
        )
