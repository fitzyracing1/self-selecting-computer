# Self-Selecting Computer (SSC)

**A computer that selects all of its own programs.**

At every boot the machine:

1. Senses its live environment (CPU, memory, observed needs)
2. Discovers every program that has *self-registered* by announcing its capabilities
3. Scores each program against the current high-level goal
4. Selects a coherent subset that fits inside a resource budget
5. Loads *only* those programs
6. Runs them cooperatively

There is no hard-coded list of required software.  
The only permanent pieces are the discovery + selection kernel.  
Everything else is chosen.

## Quick start

```bash
cd self_selecting_computer
python3 main.py                 # one-shot run
python3 main.py --terminal      # interactive terminal (recommended)
python3 main.py -t              # same as --terminal
```

Inside the terminal you can change goals on the fly, re-select, run cycles, force generation of new programs, inspect scores, etc.

Examples of goals that produce different selections:

- `"become a useful, self-monitoring, self-improving computer that reports its own state"`
- `"perform pure mathematical calculations and hashing only"`
- `"self improve by generating new code and programs while monitoring state"`
- `"connect to the internet, use a browser and report what I find online"`
- `"run an http server and serve my status to the network"`
- `"use the gpu for heavy tensor compute and matrix acceleration"`

## Architecture

```
self_selecting_computer/
├── main.py                 # entry point + interactive terminal
├── core/
│   ├── catalog.py          # ProgramMeta + dynamic discovery
│   ├── selector.py         # goal-driven scoring & selection
│   ├── computer.py         # the machine itself
│   └── terminal.py         # interactive REPL
├── programs/               # each file self-registers on import
│   ├── sys_monitor, logger, reporter, goal_keeper, …
│   ├── web_fetcher, browser, net_status
│   ├── server, gpu, file_manager, self_test, …
│   └── auto_prog_*.py      # generated at runtime
├── data/                   # boot records, status reports, kv store
├── logs/                   # event streams
└── docs/                   # GitHub Pages site
```

## How a program announces itself

```python
from core.catalog import register, ProgramMeta

register(ProgramMeta(
    name="my_tool",
    description="...",
    capabilities=["tag1", "tag2", ...],
    resource_cost=0.1,
    priority_tags=["..."],
    requires=["other_program"],   # optional
    entry_point="my_tool:run",
))

def run(context: dict, previous: dict) -> dict:
    ...
```

The computer never needs a central registry file.  
Import = announcement.

## Self-extension

When the goal or observed needs contain generation keywords,  
`code_generator` writes a brand-new program file into `programs/`.  
On the next boot that file is automatically discovered and becomes a candidate for selection.

## Live server

When the `server` program is selected it listens on port **8765**:

- `http://127.0.0.1:8765/` — HTML status page
- `/status` `/programs` `/goal` `/results` — JSON API

## Design principles

- Minimal kernel
- Programs are self-describing
- Selection is goal + environment driven
- Resource-aware
- Observable (every boot and run leaves JSON artifacts)
- Capable of growing its own software surface

This is a complete, working demonstration that a computer can choose every program it runs.
