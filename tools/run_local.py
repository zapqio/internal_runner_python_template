"""Local smoke runner; the real Zapqio runtime is supplied by the platform."""

import argparse
import importlib.util
import logging
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
LOGGER_NAME = "template-local"


def execute(data: str, method: str = "template-hello", constants=None) -> str | None:
    method_path = (ROOT / "methods" / f"{method}.py").resolve()
    if method_path.parent != (ROOT / "methods").resolve():
        raise ValueError("Choose a method directly inside methods/.")

    values = dict(constants or {})

    def get_constant(name):
        if not isinstance(name, str):
            raise TypeError("Constant name must be a string.")
        if name not in values:
            raise KeyError(f"Constant '{name}' is not defined.")
        return values[name]

    runtime = ModuleType("zapqio")
    runtime.log = logging.getLogger(LOGGER_NAME)
    runtime.constants = SimpleNamespace(get=get_constant)
    runtime.job_id = "00000000-0000-0000-0000-000000000001"
    runtime.attempt_id = "00000000-0000-0000-0000-000000000002"
    runtime.method_name = method

    spec = importlib.util.spec_from_file_location("_template_local_method", method_path)
    if spec is None or spec.loader is None:
        raise ValueError("Cannot load method.")
    module = importlib.util.module_from_spec(spec)

    with patch.dict(sys.modules, {"zapqio": runtime}), patch.object(sys, "path", [str(ROOT), *sys.path]):
        spec.loader.exec_module(module)
        result = module.run(data)

    if result is not None and not isinstance(result, str):
        raise TypeError("run(data) must return a string or None.")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a method with a local substitute for the Zapqio runtime.")
    parser.add_argument("--method", default="template-hello")
    parser.add_argument("--input", type=Path, required=True, help="UTF-8 file with the step input.")
    parser.add_argument("--demo-secret", action="store_true", help="Provide a fake EXAMPLE_API_TOKEN for this local test.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    constants = {"EXAMPLE_API_TOKEN": "local-demo-value-not-a-real-token"} if args.demo_secret else {}
    result = execute(args.input.read_bytes().decode("utf-8"), args.method, constants)
    if result is not None:
        print(result)


if __name__ == "__main__":
    main()
