"""Load pure integration modules without importing Home Assistant."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
from types import ModuleType

ROOT = Path(__file__).parents[1] / "custom_components" / "nio_telematics"


def load_module(name: str) -> ModuleType:
    """Load one module directly from its source file."""
    module_name = f"nio_telematics_test_{name}"
    spec = spec_from_file_location(module_name, ROOT / f"{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {name}")
    module = module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
