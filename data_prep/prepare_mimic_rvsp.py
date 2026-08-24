import glob, os, random
import numpy as np, pandas as pd

ROOT   = "/nfs/usrhome2/echo/mimic-iv-echo"
OUT    = "/home/abag/datasets/csv"
TARGET = "tr_mmhg"
SEED   = 0
random.seed(SEED)

# study -> list of mp4
vids = {}
for sdir in glob.glob(f"{ROOT}/videos/p*/s*"):
    mp4 = glob.glob(f"{sdir}/*.mp4")
    if mp4:
        subj = int(os.path.basename(os.path.dirname(sdir))[1:])
        stud = int(os.path.basename(sdir)[1:])
        vids[(subj, stud)] = mp4
print(f"studies with mp4: {len(vids)}")

# measurement_id -> (subject, study)
sl = pd.read_csv(f"{ROOT}/v1.0/echo-study-list.csv").dropna(subset=["measurement_id"])
sl["measurement_id"] = sl["measurement_id"].astype(int)
mid2study = {r.measurement_id: (r.subject_id, r.study_id)
             for r in sl.itertuples() if (r.subject_id, r.study_id) in vids}
print(f"measurement_ids with video: {len(mid2study)}")

# pull the target
keep = []
for chunk in pd.read_csv(f"{ROOT}/v1.0/structured-measurement.csv", chunksize=2_000_000,
        usecols=["measurement_id","measurement","result"]):
    c = chunk[(chunk.measurement == TARGET) &
              chunk.measurement_id.isin(mid2study) &
              chunk.result.notna()]
    if len(c): keep.append(c)
m = pd.concat(keep)
m["val"] = pd.to_numeric(m.result, errors="coerce")
m = m.dropna(subset=["val"]).groupby("measurement_id", as_index=False).val.mean()
print(f"studies with {TARGET}: {len(m)}")

# one random clip per study
rows = []
for r in m.itertuples():
    key = mid2study[r.measurement_id]
    rows.append((random.choice(vids[key]), r.val, key[0]))
print(f"rows: {len(rows)}")

# split by SUBJECT, not study
subs = sorted({s for _, _, s in rows})
rng = np.random.default_rng(SEED); rng.shuffle(subs)
n = len(subs); ntr, nva = int(.7*n), int(.15*n)
grp = {s: ("train" if i < ntr else "val" if i < ntr+nva else "test")
       for i, s in enumerate(subs)}

splits = {"train": [], "val": [], "test": []}
for p_, v, s in rows:
    splits[grp[s]].append((p_, v))

os.makedirs(OUT, exist_ok=True)
for k, rr in splits.items():
    fp = f"{OUT}/mimic_{TARGET}_{k}.csv"
    with open(fp, "w") as f:
        for p_, v in rr: f.write(f"{p_} {v}\n")
    print(f"{fp}: {len(rr)} rows")

tr = np.array([v for _, v in splits["train"]])
print("\n" + "="*50)
print(f"target_mean: {tr.mean():.4f}")
print(f"target_std:  {tr.std(ddof=1):.4f}")
print("="*50)
