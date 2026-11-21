"""Prove the regression fixture fails against the previous released sources."""

import subprocess
import sys
import urllib.request
from pathlib import Path

paths = [
    "custom_components/nio_telematics/api.py",
    "custom_components/nio_telematics/coordinator.py",
]
saved = {path: Path(path).read_bytes() for path in paths}
try:
    for path in paths:
        with urllib.request.urlopen(
            "https://raw.githubusercontent.com/nicolasvangeluwe/nio-home-assistant/"
            "0f5a862c37dda6335cbd2e781a80def43cb24c34/" + path,
            timeout=30,
        ) as response:
            Path(path).write_bytes(response.read())
    baseline = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_coordinator.py::test_generic_cell_404_does_not_lock_direct_polling",
            "-q",
        ],
        capture_output=True,
        text=True,
    )
    print(baseline.stdout)
    print(baseline.stderr)
    if (
        baseline.returncode != 1
        or "test_generic_cell_404_does_not_lock_direct_polling" not in baseline.stdout
        or "FAILED" not in baseline.stdout
        or "HTTP 404" not in baseline.stdout
    ):
        raise RuntimeError(
            "Legacy source did not reproduce the expected HTTP404 failure"
        )
    print("Confirmed prior release fails the identical generic-404 replay.")
finally:
    for path, content in saved.items():
        Path(path).write_bytes(content)
