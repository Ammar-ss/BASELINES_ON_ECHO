import argparse, os, numpy as np, pandas as pd
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--target", default="LVIDd")
ap.add_argument("--csv", default="/home/abag/datasets/echonet-lvf/MeasurementsList.csv")
ap.add_argument("--video_dir", default="/home/abag/datasets/echonet-lvf/all_videos")
ap.add_argument("--out", default="/home/abag/datasets/csv")
a = ap.parse_args()

df = pd.read_csv(a.csv)
sub = df[df["Calc"].astype(str) == a.target][["HashedFileName","CalcValue","split"]].dropna()
sub["CalcValue"] = pd.to_numeric(sub["CalcValue"], errors="coerce")
sub = sub.dropna()
sub = sub.groupby("HashedFileName", as_index=False).agg({"CalcValue":"mean","split":"first"})
print(f"{a.target}: {len(sub)} unique videos")

vdir = Path(a.video_dir)
splits = {"train":[], "val":[], "test":[]}
missing = 0
for _, r in sub.iterrows():
    p = vdir / (str(r["HashedFileName"]) + ".avi")
    if not p.exists():
        missing += 1; continue
    s = str(r["split"]).lower()
    key = {"train":"train","val":"val","validation":"val","test":"test"}.get(s)
    if key is None: continue
    splits[key].append((str(p.resolve()), float(r["CalcValue"])))
print(f"missing videos: {missing}")

os.makedirs(a.out, exist_ok=True)
for name, rr in splits.items():
    fp = f"{a.out}/lvh_{a.target}_{name}.csv"
    with open(fp, "w") as f:
        for p, v in rr: f.write(f"{p} {v}\n")
    print(f"{fp}: {len(rr)} rows")

tr = np.array([v for _, v in splits["train"]])
print("\n" + "="*50)
print(f"target_mean: {tr.mean():.4f}")
print(f"target_std:  {tr.std(ddof=1):.4f}")
print(f"range: {tr.min():.2f} to {tr.max():.2f}")
print("="*50)
