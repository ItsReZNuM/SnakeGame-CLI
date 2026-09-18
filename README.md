# SnakeGame CLI

[![PyPI version](https://img.shields.io/pypi/v/reznum-snakegame.svg)](https://pypi.org/project/reznum-snakegame/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Star](https://img.shields.io/badge/GitHub-Star%20Repo-yellow.svg)](https://github.com/ItsReZNuM/SnakeGame-CLI)

A complete, polished, retro arcade Snake game for your terminal, engineered in Python using the [Rich](https://github.com/Textualize/rich) library.

Built with extensive customization, 5 vibrant color themes, an interactive main menu, real-time terminal size detection, timed SuperFood events, and high-score tracking. Designed for Windows (Command Prompt, PowerShell, Windows Terminal) with native support for POSIX environments (Linux, macOS).

---

## Features

- **Interactive Main Menu**: Navigate like a full arcade game:
  - `Start Game`: Launch directly into the action.
  - `Settings`: Adjust arena width, height, initial speed, color themes, and toggle bonus SuperFoods.
  - `About Creator`: View developer links and social channels.
  - `Exit`: Cleanly leave the application.
- **5 Beautiful Color Themes**:
  - `Nokia Classic`: Retro green and yellow arcade aesthetic.
  - `Cyberpunk Neon`: Vibrant cyan, magenta, and yellow.
  - `Retro Amber`: Warm gold, amber, and red.
  - `Synthwave`: Electric magenta, purple, and cyan.
  - `Matrix Monochrome`: High-contrast minimal white.
- **Timed SuperFood Bonus**:
  - A glowing SuperFood (`★`) spawns after every 5 regular foods eaten.
  - Features an active **5-second countdown timer**.
  - Awards **+50 bonus points** and **+3 length growth** if eaten before time runs out.
- **Live Terminal Dimension Reader**:
  - Settings screen monitors console width and height in real time.
  - Alerts you if the terminal window is too small for the selected arena dimensions.
- **Responsive Controls & Turn Buffering**:
  - Fully supports both **Arrow Keys** (`↑`, `↓`, `←`, `→`) and **W / A / S / D**.
  - Built-in turn buffering prevents rapid opposite-direction reversals into the snake's neck.
- **Persistent High Scores & Settings**:
  - Automatically saves best scores to `~/.snakegame/scores.json`.
  - Automatically remembers your customized settings in `~/.snakegame/settings.json`.
- **Accurate Gameplay Timer**:
  - Millisecond-precision active timer (`MM:SS`) that pauses when you pause or browse menus.
- **Polished CLI**:
  - Custom Rich-rendered `--help` guide, `--theme` flag, and user-friendly error messages without Python tracebacks.

---

## Preview

```text
  ╔═══════════════════════════════════════════════════╗
  ║                S N A K E   G A M E                ║
  ║                  Terminal CLI Edition             ║
  ╚═══════════════════════════════════════════════════╝

╭──────────────── Snake Game CLI ────────────╮
│                                            │
│            ██████████                      │
│                     █                      │
│                     █      ◆        ★      │
│                                            │
╰────────────────────────────────────────────╯
╭────────────────────────────────────────────╮
│  SCORE: 60   BEST: 150   TIME: 01:24       │
│  SPEED: 7.8/s            LENGTH: 9         │
│  ★ SUPERFOOD: 3.4s (+50 PTS) ★             │
│  Controls: [WASD / Arrows] Move  [P] Pause │
╰────────────────────────────────────────────╯
```

---

## Requirements

- Python **3.8+**
- `rich >= 13.0.0`
- Operating System:
  - Windows 10/11 (Windows Terminal, PowerShell, CMD)
  - Linux / macOS

---

## Installation

### Install via pip (PyPI)

```bash
pip install reznum-snakegame
```

### Install from Source

```bash
# Clone repository
git clone https://github.com/ItsReZNuM/SnakeGame-CLI.git
cd SnakeGame-CLI

# Install package
pip install .
```

For editable development mode:

```bash
pip install -e .
```

---

## Usage

Launch directly via the console command:

```bash
snakegame
```

Or execute as a Python module:

```bash
python -m snakegame
```

---

## CLI Options

```text
Usage:  snakegame [OPTIONS]
Module: python -m snakegame [OPTIONS]

Options:
  -w, --width <int>     Grid width in cells (range: 10 - 60, default: 24)
  -H, --height <int>    Grid height in cells (range: 8 - 35, default: 16)
  -s, --speed <float>   Initial speed in moves/second (range: 1.0 - 25.0, default: 6.0)
  -t, --theme <str>     Color theme: Nokia Classic, Cyberpunk Neon, Retro Amber,
                        Synthwave, Matrix Monochrome
  --no-color            Disable terminal colors (monochrome mode)
  -v, --version         Display version information and exit
  -h, --help            Show the polished Rich help guide and exit
```

### Examples

Run standard game with Main Menu:
```bash
snakegame
```

Start with Cyberpunk Neon theme:
```bash
snakegame --theme "Cyberpunk Neon"
```

Play on a larger arena:
```bash
snakegame --width 32 --height 20
```

Fast challenge mode:
```bash
snakegame --speed 10.0
```

---

## Controls

| Action | Primary Keys | Alternative Keys |
| :--- | :--- | :--- |
| **Move / Menu Navigate** | `↑` `↓` `←` `→` (Arrow Keys) | Custom Keys (`W` `A` `S` `D` default) |
| **Select / Confirm** | `Enter` | `Spacebar` |
| **Back / Cancel** | `ESC` | `B` / `Backspace` |
| **Pause / Resume** | `Spacebar` | `ESC` / `P` |
| **Restart Game** | `R` *(after Game Over)* | `Enter` / `Spacebar` |
| **Main Menu** | `M` *(after Game Over or Pause)* | `ESC` |
| **Quit** | `Q` | `ESC` (on Menu/GameOver) |

> 💡 **Custom Keybindings**: Configure your custom controls anytime from **Settings → Keybindings**! Changes are automatically saved to `~/.snakegame/settings.json`.

---

## About the Creator

Made with ❤️ by **ItsReZNuM**

- **GitHub Profile**: [https://github.com/ItsReZNuM](https://github.com/ItsReZNuM)
- **Repository**: [https://github.com/ItsReZNuM/SnakeGame-CLI](https://github.com/ItsReZNuM/SnakeGame-CLI)
- **Telegram**: [@ItsReZNuM](https://t.me/ItsReZNuM)
- **Instagram**: [@rez.num](https://instagram.com/rez.num)

⭐ **Enjoyed the game?** Please consider giving the repository a star on GitHub! It means a lot and helps support future development.

---

## Development & Testing

Run all 38 automated unit tests with `pytest`:

```bash
pytest -v
```

Build source distribution and wheels:

```bash
python -m build
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
