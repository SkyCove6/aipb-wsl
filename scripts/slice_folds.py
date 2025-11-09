import argparse
import math
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Split wf_jobs.tsv into smaller jobs per fold.")
    parser.add_argument("--config", required=True, help="Input wf_jobs.tsv path")
    parser.add_argument("--out", required=True, help="Output TSV path")
    parser.add_argument("--parts", type=int, default=3, help="Slices per fold (default: %(default)s)")
    args = parser.parse_args()

    src = Path(args.config).expanduser().resolve()
    dst = Path(args.out).expanduser().resolve()
    parts = max(1, args.parts)

    rows = []
    for line in src.read_text().splitlines():
        name, s, e, trade = line.split("\t")
        s, e, trade = int(s), int(e), int(trade)
        span = e - s
        step = math.ceil(span / parts)
        for i in range(parts):
            ss = s + i * step
            ee = min(e, s + (i + 1) * step - 1)
            if ss > ee:
                continue
            tt = max(trade, ss)
            rows.append((f"{name}_p{i + 1}", ss, ee, tt))

    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w") as w:
        for r in rows:
            w.write(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\n")
    print(f"Wrote {dst} with {len(rows)} jobs.")


if __name__ == "__main__":
    main()
