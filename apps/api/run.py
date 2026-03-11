"""Run API with src/ on PYTHONPATH so imports are from src/ root."""
import os
import subprocess
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.join(_ROOT, "src")
env = os.environ.copy()
env["PYTHONPATH"] = _SRC + os.pathsep + env.get("PYTHONPATH", "")

sys.exit(
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload"],
        env=env,
        cwd=_ROOT,
    ).returncode
)
