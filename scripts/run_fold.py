#!/usr/bin/env python3
import argparse
import sys
import subprocess
import tempfile
import yaml
import os
from pathlib import Path

repo = Path("/mnt/d/ai-profit-bot-folder")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a single backtest fold")
    parser.add_argument("name", help="Fold name")
    parser.add_argument("start_ts", type=int, help="Inclusive start timestamp")
    parser.add_argument("end_ts", type=int, help="Inclusive end timestamp")
    parser.add_argument("trade_start_ts", type=int, help="Trading start timestamp")
    parser.add_argument(
        "--ticks",
        default=str(Path.home() / "aipb-data" / "ticks_all.csv"),
        help="Ticks CSV to use (default: %(default)s)",
    )
    return parser.parse_args()


args = parse_args()
ticks = str(Path(args.ticks).expanduser())
name = args.name
start = args.start_ts
end = args.end_ts
trade = args.trade_start_ts

print(f"RUN {name} {start} {end} {trade}", flush=True)

grid = {
    "scenarios": [
        {
            "name": name,
            "params": {
                "start_ts": start,
                "end_ts": end,
                "trade_start_ts": trade,
            },
        }
    ]
}

with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yaml") as tf:
    yaml.safe_dump(grid, tf, sort_keys=False)
    grid_path = tf.name

env = os.environ.copy()
env["RUNS_DIR"] = str(Path.home() / "runs")

py_path = env.get("PYTHONPATH", "")
if "/mnt/d/ai-profit-bot-folder" not in py_path.split(":"):
    env["PYTHONPATH"] = (py_path + ":" if py_path else "") + "/mnt/d/ai-profit-bot-folder"

for k in [
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
]:
    env.setdefault(k, "1")

cmd = [
    sys.executable,
    "-u",
    "-m",
    "backtest.engine",
    "--ticks",
    ticks,
    "--grid",
    grid_path,
    "--settings",
    str(repo / "config/app.yaml"),
    "--progress-sec",
    "10",
]
print("Running:", " ".join(cmd))
rc = subprocess.run(cmd, cwd=str(repo), env=env, check=False).returncode
sys.exit(rc)
