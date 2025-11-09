from pathlib import Path
import sys

repo = Path("/mnt/d/ai-profit-bot-folder")
sys.path.insert(0, str(repo))  # make project modules importable

from backtest.data import stream_ticks
from backtest.engine import build_walk_forward_folds
from ai_profit_bot.config import load_settings

ticks = Path("/mnt/d/aipb-wsl/aipb-data/ticks_all.csv")

settings = load_settings(str(repo/"config/app.yaml"))
folds    = int(settings.backtest["folds"])
embargo  = float(settings.backtest["embargo_days"])

first_ts = last_ts = None
for t in stream_ticks(ticks):
    if first_ts is None: first_ts = t.ts
    last_ts = t.ts
if first_ts is None:
    raise SystemExit("no ticks found")

out = Path("/mnt/d/aipb-wsl/wf_jobs.tsv")
with out.open("w") as w:
    for f in build_walk_forward_folds(first_ts, last_ts, folds, embargo):
        w.write(f"{f.name}\t{int(f.test_start)}\t{int(f.test_end)}\t{int(f.trade_start)}\n")
print(f"Wrote {out}")
