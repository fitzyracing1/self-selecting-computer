"""
SelfSelectingComputer

A computer that, at every boot, selects the complete set of programs
it will run. Nothing is pre-installed except the selector kernel itself.
Programs announce themselves; the selector chooses which ones to load
and execute based on the goal + live environment context.
"""

from __future__ import annotations
import os
import sys
import time
import json
import platform
import psutil
import importlib
from typing import Dict, List, Any, Optional
from pathlib import Path

from .catalog import discover_programs, PROGRAM_REGISTRY, get_program
from .selector import ProgramSelector


class SelfSelectingComputer:
    def __init__(self, name: str = "SSC-1", goal: str = "become useful and self-aware"):
        self.name = name
        self.goal = goal
        self.boot_time = time.time()
        self.selected_programs: List[str] = []
        self.loaded: Dict[str, Any] = {}
        self.context: Dict[str, Any] = {}
        self.logs: List[str] = []
        self.selector = ProgramSelector(max_resource_budget=0.90)
        self.root = Path(__file__).resolve().parent.parent
        self.data_dir = self.root / "data"
        self.log_dir = self.root / "logs"
        self.data_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)

    def log(self, msg: str):
        ts = time.strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        self.logs.append(line)
        print(line)

    def sense_environment(self) -> Dict[str, Any]:
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        ctx = {
            "hostname": platform.node(),
            "os": f"{platform.system()} {platform.release()}",
            "python": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "mem_total_gb": round(mem.total / (1024**3), 2),
            "mem_available_gb": round(mem.available / (1024**3), 2),
            "free_resource_ratio": mem.available / mem.total,
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "boot_epoch": self.boot_time,
            "goal": self.goal,
            "observed_needs": [],
        }
        if mem.percent > 70:
            ctx["observed_needs"].append("memory pressure")
        if disk.percent > 80:
            ctx["observed_needs"].append("storage pressure")
        if psutil.cpu_percent(interval=0.05) > 50:
            ctx["observed_needs"].append("cpu busy")
        ctx["observed_needs"].extend(["self monitoring", "logging", "reporting"])
        self.context = ctx
        return ctx

    def boot(self) -> None:
        self.log(f"=== {self.name} BOOTING ===")
        self.log(f"Goal: {self.goal}")
        self.log("Sensing environment...")
        ctx = self.sense_environment()
        self.log(f"  CPU: {ctx['cpu_count']} cores @ {ctx['cpu_percent']}%")
        self.log(f"  RAM: {ctx['mem_available_gb']} / {ctx['mem_total_gb']} GB free")
        self.log(f"  Observed needs: {', '.join(ctx['observed_needs'])}")

        self.log("Discovering available programs (self-registration)...")
        discover_programs()
        self.log(f"  Found {len(PROGRAM_REGISTRY)} programs that announced themselves")

        self.log("Selecting complete software complement...")
        selected = self.selector.select(self.goal, ctx, force_include=[])
        self.selected_programs = selected
        self.log(self.selector.explain())

        self.log("Loading selected programs...")
        for name in selected:
            self._load(name)

        self.log(f"Boot complete. {len(self.loaded)} programs active.")
        self._write_boot_record()

    def _load(self, name: str) -> None:
        meta = get_program(name)
        if not meta or not meta.entry_point:
            self.log(f"  [skip] {name}: no entry_point")
            return
        try:
            mod_name, func_name = meta.entry_point.split(":")
            full_mod = f"programs.{mod_name}" if not mod_name.startswith("programs") else mod_name
            mod = importlib.import_module(full_mod)
            func = getattr(mod, func_name)
            self.loaded[name] = func
            self.log(f"  loaded {name} → {meta.entry_point}")
        except Exception as e:
            self.log(f"  [fail] {name}: {e}")

    def run(self, cycles: int = 3) -> None:
        if not self.loaded:
            self.log("No programs loaded — nothing to run.")
            return
        self.log(f"=== RUNNING {cycles} cycles ===")
        results = {}
        for cycle in range(1, cycles + 1):
            self.log(f"-- cycle {cycle} --")
            for name, entry in self.loaded.items():
                try:
                    out = entry(self.context, results)
                    results[name] = out
                    self.log(f"  {name}: {str(out)[:120]}")
                except Exception as e:
                    self.log(f"  {name} ERROR: {e}")
            time.sleep(0.15)
        self.log("=== RUN COMPLETE ===")
        self._write_results(results)

    def _write_boot_record(self):
        record = {
            "name": self.name,
            "goal": self.goal,
            "boot_time": self.boot_time,
            "selected": self.selected_programs,
            "context": {k: v for k, v in self.context.items() if k != "goal"},
            "scores": self.selector.scores,
        }
        path = self.data_dir / "last_boot.json"
        path.write_text(json.dumps(record, indent=2, default=str))
        self.log(f"Boot record → {path}")

    def _write_results(self, results: Dict):
        path = self.data_dir / "last_run.json"
        path.write_text(json.dumps(results, indent=2, default=str))
        self.log(f"Run results → {path}")

    def status(self) -> str:
        lines = [
            f"Computer: {self.name}",
            f"Goal: {self.goal}",
            f"Selected programs: {', '.join(self.selected_programs) or '(none)'}",
            f"Loaded: {list(self.loaded.keys())}",
            f"Uptime: {time.time() - self.boot_time:.1f}s",
        ]
        return "\n".join(lines)
