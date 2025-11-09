from pathlib import Path
import math

parts = 3  # slices per fold (tune 2–4)
src = Path("/mnt/d/aipb-wsl/wf_jobs.tsv")
dst = Path("/mnt/d/aipb-wsl/wf_jobs_sliced.tsv")

rows = []
for line in src.read_text().splitlines():
    name,s,e,trade = line.split("\t")
    s,e,trade = int(s),int(e),int(trade)
    span = e - s
    step = math.ceil(span/parts)
    for i in range(parts):
        ss = s + i*step
        ee = min(e, s + (i+1)*step - 1)
        tt = max(trade, ss)
        rows.append((f"{name}_p{i+1}", ss, ee, tt))

with dst.open("w") as w:
    for r in rows:
        w.write(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\n")
print(f"Wrote {dst} with {len(rows)} jobs.")
