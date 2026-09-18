# SnakeGame CLI

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style: Clean](https://img.shields.io/badge/code%20style-clean-brightgreen.svg)](#)

A polished, responsive terminal-based Snake game inspired by the classic Nokia 3310 experience, engineered entirely in Python with the [Rich](https://github.com/Textualize/rich) library.

Targeted primarily for Windows (Command Prompt, PowerShell, and Windows Terminal) while maintaining POSIX compatibility (Linux, macOS), SnakeGame CLI delivers authentic arcade gameplay, dynamic speed scaling, local high-score persistence, and a custom visual interface without external GUI frameworks.

---

## Features

- **Authentic Nokia Gameplay**: Continuous grid movement, classic collision dynamics (walls and self-collision), and guaranteed vacant-cell food placement.
- **Responsive Controls**: Instant, non-blocking keyboard input with turn buffering to prevent rapid double-turn reversals into the snake's neck.
- **Rich Terminal UI**: Rendered with Rich panels, tables, live refresh buffering, and retro arcade aesthetics.
- **Accurate Game Timer**: Real-time timer (`MM:SS`) measuring active gameplay, pausing automatically when the game is paused.
- **Adaptive Difficulty**: Movement speed dynamically scales as food is consumed, up to a configurable ceiling.
- **Persistent High Scores**: Automatically saves your best records to a local JSON file (`~/.snakegame/scores.json`).
- **Flexible Controls**: Simultaneous support for Arrow Keys (`↑`, `↓`, `←`, `→`) and `W`/`A`/`S`/`D`.
- **Polished CLI**: Rich-rendered `--help` guide with parameter boundaries, usage examples, and clean error messages without Python tracebacks.
- **PyPI-Ready Package Architecture**: Structured with PEP 517/621 `pyproject.toml` and standard entry points.

---

## Preview

```text
  ╔════════════════════════════════════════╗
  ║        S N A K E   C L A S S I C       ║
  ║       Retro Nokia 3310 Edition         ║
  ╚════════════════════════════════════════╝

╭──────────────── NOKIA 3310 ────────────────╮
│                                            │
│            ██████████                      │
│                     █                      │
│                     █      ◆               │
│                                            │
╰────────────────────────────────────────────╯
╭────────────────────────────────────────────╮
│  SCORE: 40   BEST: 120   TIME: 01:14       │
│  SPEED: 7.2/s            LENGTH: 7         │
│  Controls: [WASD / Arrows] Move  [P] Pause │
╰────────────────────────────────────────────╯
```
*(Rendered directly in your terminal using Rich)*

---

## Requirements

- Python **3.8+**
- `rich >= 13.0.0`
- Operating System:
  - Windows (Windows Terminal, CMD, PowerShell) — *Primary target*
  - Linux / macOS (standard ANSI/xterm terminals supported via non-blocking I/O)

---

## Installation

### Install from Local Source

Clone the repository and install in editable development mode or standard mode:

```bash
# Clone the repository
git clone https://github.com/example/SnakeGame-CLI.git
cd SnakeGame-CLI

# Install the package locally
pip install .
```

For active development with immediate code reflection:

```bash
pip install -e .
```

---

## Usage

Once installed, launch the game directly using the registered console script:

```bash
snakegame
```

Or execute it as a Python module:

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
  --no-color            Disable terminal colors (monochrome mode)
  -v, --version         Display version information and exit
  -h, --help            Show the polished Rich help guide and exit
```

### Examples

Run standard game:
```bash
snakegame
```

Play on a larger arena:
```bash
snakegame --width 32 --height 20
```

Start with a high initial speed for a fast-paced challenge:
```bash
snakegame --speed 10.0
```

Run in monochrome mode:
```bash
snakegame --no-color
```

View the Rich help manual:
```bash
snakegame --help
```

---

## Controls

| Action | Primary Keys | Alternative Keys |
| :--- | :--- | :--- |
| **Move Up** | `↑` (Up Arrow) | `W` / `w` |
| **Move Down** | `↓` (Down Arrow) | `S` / `s` |
| **Move Left** | `←` (Left Arrow) | `A` / `a` |
| **Move Right** | `→` (Right Arrow) | `D` / `d` |
| **Start / Resume** | `Spacebar` | `Enter` |
| **Pause Game** | `P` / `p` | `Spacebar` |
| **Restart Game** | `R` / `r` *(after Game Over)* | `Spacebar` |
| **Quit Game** | `Q` / `q` | `Escape` (`ESC`) |

---

## Project Architecture

The codebase separates concerns across isolated, single-responsibility modules:

```text
SnakeGame-CLI/
├── pyproject.toml           # Build system, metadata & console entry points
├── requirements.txt         # Core dependencies
├── LICENSE                  # MIT License
├── README.md                # Project documentation
├── src/
│   └── snakegame/
│       ├── __init__.py      # Package metadata & version
│       ├── __main__.py      # python -m snakegame entry point
│       ├── cli.py           # Rich-formatted help, CLI arguments & validation
│       ├── config.py        # GameConfig dataclass & parameter bounds checking
│       ├── board.py         # Grid boundaries & cell query abstractions
│       ├── snake.py         # Snake segments deque, direction constraints & collision logic
│       ├── food.py          # Random food spawner ensuring vacant placement
│       ├── storage.py       # High-score JSON persistence (~/.snakegame/scores.json)
│       ├── input.py         # Non-blocking cross-platform input handler
│       ├── ui.py            # Rich rendering: board, stats panel, start/over screens
│       └── game.py          # State machine, high-precision timer, tick loop & cleanup
└── tests/
    ├── __init__.py
    ├── test_snake.py        # Snake movements, turns, length growth, self-collision
    ├── test_board.py        # Boundary checks & empty cell calculations
    ├── test_food.py         # Food placement & saturated board edge case
    ├── test_storage.py      # High-score loading, saving & corrupted JSON fallback
    ├── test_config.py       # GameConfig parameter validations & boundary constraints
    └── test_game.py         # Game states, speed scaling, and timer formatting
```

---

## Development & Testing

### Running Tests

Automated tests are written with `pytest`. Run the full test suite with:

```bash
pytest -v
```

### Building the Package

To build source distribution and binary wheels:

```bash
# Install build tool if needed
pip install build

# Build the package
python -m build
```

Artifacts will be generated in `dist/`:
- `dist/snakegame_cli-0.1.0-py3-none-any.whl`
- `dist/snakegame_cli-0.1.0.tar.gz`

---

## Roadmap

- [ ] Obstacle maps and custom maze presets.
- [ ] Sound effects via terminal bell or optional audio sidecar.
- [ ] Multi-food variations (bonus time-limited golden fruit).
- [ ] Ghost snake / replay mode for personal bests.

---

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Run tests (`pytest`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
