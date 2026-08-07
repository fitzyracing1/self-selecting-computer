"""
Program Catalog for the Self-Selecting Computer.

Each program declares its own metadata so the computer can choose
without any external hard-coded list of required software.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable, Optional
import importlib
import inspect


@dataclass
class ProgramMeta:
    name: str
    description: str
    capabilities: List[str]
    resource_cost: float          # 0.0 – 1.0 relative load
    priority_tags: List[str]
    requires: List[str] = field(default_factory=list)
    entry_point: Optional[str] = None   # "module:func"
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "resource_cost": self.resource_cost,
            "priority_tags": self.priority_tags,
            "requires": self.requires,
            "entry_point": self.entry_point,
            "version": self.version,
        }


# The computer discovers these by scanning the programs/ package.
# No master list is hard-coded into the kernel; discovery is dynamic.
PROGRAM_REGISTRY: Dict[str, ProgramMeta] = {}


def register(meta: ProgramMeta):
    """Programs call this at import time to announce themselves."""
    PROGRAM_REGISTRY[meta.name] = meta


def discover_programs(package_path: str = "programs") -> Dict[str, ProgramMeta]:
    """
    Dynamically import every module under programs/ so each can
    self-register. This is the only place the computer learns
    what programs exist.
    """
    import pkgutil
    import sys
    import os

    # Ensure the package is on path
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if base not in sys.path:
        sys.path.insert(0, base)

    package = importlib.import_module(package_path)
    for _, modname, ispkg in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
        if not ispkg:
            try:
                importlib.import_module(modname)
            except Exception as e:
                print(f"[catalog] failed to load {modname}: {e}")
    return dict(PROGRAM_REGISTRY)


def get_program(name: str) -> Optional[ProgramMeta]:
    return PROGRAM_REGISTRY.get(name)
