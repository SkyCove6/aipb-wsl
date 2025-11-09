from pathlib import Path
import subprocess, sys

# Make project modules importable
repo = Path("/mnt/d/ai-profit-bot-folder")
sys.path.insert(0, str(repo))

from backtest.engine import build_walk_forward_folds
from ai_profit_bot.config import load_settings

ticks_path = str(Path.home() / "aipb-data" / "ticks_all.csv")

# Get first and last timestamp (ms) using shell tools (fast)
first_ms = int(subprocess.check_output(
    ["bash","-lc", f"awk -F, 'NR==2{{print $1; exit}}' {ticks_path}"]
).decode().strip())

last_ms = int(subprocess.check_output(
    ["bash","-lc", f"tail -n 1 {ticks_path} | cut -d, -f1"]
).decode().strip())

first_ts = first_ms/1000.0
last_ts  = last_ms/1000.0

settings = load_settings(str(repo/"config/app.yaml"))
folds   = int(settings.backtest["folds"])
embargo = float(settings.backtest["embargo_days"])

out = Path("/mnt/d/aipb-wsl/wf_jobs.tsv")
with out.open("w") as w:
    for f in build_walk_forward_folds(first_ts, last_ts, folds, embargo):
        w.write(f"{f.name}\t{int(f.test_start)}\t{int(f.test_end)}\t{int(f.trade_start)}\n")

print(f"Wrote {out}")
