#!/usr/bin/env python3
"""
Self-Selecting Computer — main entry point.

This computer chooses every program it runs.
At boot it:
  1. Senses its environment
  2. Discovers every program that has self-registered
  3. Scores and selects a coherent set under a resource budget
  4. Loads only those programs
  5. Runs them cooperatively for a few cycles

No program is hard-wired into the kernel except the discovery + selection machinery.

Use --terminal (or -t) for an interactive command loop.
"""

import sys
import os

# Make the package importable when run from the project root
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.computer import SelfSelectingComputer
from core.terminal import Terminal


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Self-Selecting Computer — chooses all of its own programs"
    )
    parser.add_argument(
        "--goal", "-g",
        default="become a useful, self-monitoring, self-improving computer that reports its own state",
        help="High-level goal that drives program selection"
    )
    parser.add_argument("--cycles", "-c", type=int, default=2, help="Number of cooperative run cycles")
    parser.add_argument("--name", default="SSC-Prime", help="Computer name")
    parser.add_argument(
        "--terminal", "-t",
        action="store_true",
        help="Launch interactive terminal instead of one-shot run"
    )
    args = parser.parse_args()

    if args.terminal:
        computer = SelfSelectingComputer(name=args.name, goal=args.goal)
        term = Terminal(computer)
        term.start()
        return

    # One-shot mode (original behaviour)
    computer = SelfSelectingComputer(name=args.name, goal=args.goal)
    computer.boot()
    print()
    print(computer.status())
    print()
    computer.run(cycles=args.cycles)
    print()
    print("=== Final status ===")
    print(computer.status())
    print()
    print("Artifacts written under data/ and logs/")
    print("For interactive use:  python3 main.py --terminal")
    print("Or:                   python3 main.py -t")


if __name__ == "__main__":
    main()
