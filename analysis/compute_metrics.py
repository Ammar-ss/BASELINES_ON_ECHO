import os
import numpy as np
import pandas as pd

PRED = "/home/abag/REPRODUCED/results/preds"
OUT  = "/home/abag/REPRODUCED/results/metrics.csv"

CELLS = [
    ("probed_EF_dynamic_full.csv",   "probed", 55.7776, 12.4072, "PanEcho",    "EchoNet-Dynamic", "EF",    "%"),
    ("probed_LVIDd_lvh_full.csv",    "probed",  4.7050,  0.8335, "PanEcho",    "EchoNet-LVH",     "LVIDd", "cm"),
    ("probed_LVEDD_mimic_full.csv",  "probed",  4.5598,  0.7892, "PanEcho",    "MIMIC",           "LVEDD", "cm"),
    ("probed_lvedd_mimic_full.csv",  "probed",  4.5598,  0.7892, "PanEcho",    "MIMIC",           "LVEDD", "cm"),
    ("probed_RVSP_mimic_full.csv",   "probed", 29.7619, 11.7233, "PanEcho",    "MIMIC",           "RVSP",  "mmHg"),
    ("probed_EF_dynamic_ep.csv",     "probed", 55.7776, 12.4072, "EchoPrime",  "EchoNet-Dynamic", "EF",    "%"),
    ("probed_LVIDd_lvh_ep.csv",      "probed",  4.7050,  0.8335, "EchoPrime",  "EchoNet-LVH",     "LVIDd", "cm"),
    ("probed_LVEDD_mimic_ep.csv",    "probed",  4.5598,  0.7892, "EchoPrime",  "MIMIC",           "LVEDD", "cm"),
    ("probed_EF_dynamic_ej.csv",     "probed", 55.7776, 12.4072, "EchoJEPA",   "EchoNet-Dynamic", "EF",    "%"),
    ("probed_LVIDd_lvh_ej.csv",      "probed",  4.7050,  0.8335, "EchoJEPA",   "EchoNet-LVH",     "LVIDd", "cm"),
    ("zeroshot_EF_dynamic.csv",      "zs",     None,    None,    "PanEcho-ZS", "EchoNet-Dynamic", "EF",    "%"),
    ("zeroshot_LVIDd_lvh.csv",       "zs",     None,    None,    "PanEcho-ZS", "EchoNet-LVH",     "LVIDd", "cm"),
    ("zeroshot_LVIDd_mimic.csv",     "zs",     None,    None,    "PanEcho-ZS", "MIMIC",           "LVEDD", "cm"),
    ("zeroshot_RVSP_mimic.csv",      "zs",     None,    None,    "PanEcho-ZS", "MIMIC",           "RVSP",  "mmHg"),
]

rows = []
seen = set()

for fname, mode, mean, std, model, dataset, target, unit in CELLS:
    path = os.path.join(PRED, fname)
    if not os.path.exists(path):
        continue
    key = (model, dataset, target)
    if key in seen:
        continue
    df = pd.read_csv(path)
    if mode == "probed":
        truth = (df["label_real"].to_numpy(dtype=float) - mean) / std
        pred  = (df["pred_real"].to_numpy(dtype=float)  - mean) / std
    else:
        truth = df["label"].to_numpy(dtype=float)
        pred  = df["pred"].to_numpy(dtype=float)
    good = np.isfinite(truth) & np.isfinite(pred)
    truth, pred = truth[good], pred[good]
    if len(truth) < 30:
        continue
    seen.add(key)
    mae      = float(np.mean(np.abs(truth - pred)))
    baseline = float(np.mean(np.abs(truth - truth.mean())))
    ss_res   = float(np.sum((truth - pred) ** 2))
    ss_tot   = float(np.sum((truth - truth.mean()) ** 2))
    r2       = 1.0 - ss_res / ss_tot
    rows.append({
        "model": model, "dataset": dataset, "target": target, "unit": unit,
        "n": len(truth),
        "mae": mae,
        "r2": r2,
        "bias": float(pred.mean() - truth.mean()),
        "sd_label": float(truth.std(ddof=1)),
        "sd_pred": float(pred.std(ddof=1)),
        "spread": float(pred.std(ddof=1) / truth.std(ddof=1)),
        "mean_only": baseline,
        "vs_mean_pct": (1.0 - mae / baseline) * 100.0,
    })

t = pd.DataFrame(rows)
if t.empty:
    print("no prediction files found in", PRED)
    raise SystemExit
t = t.sort_values(["target", "dataset", "model"]).reset_index(drop=True)

print()
print(f"{'model':11s} {'dataset':17s} {'target':6s} {'n':>5s} {'MAE':>8s} "
      f"{'R2':>7s} {'bias':>8s} {'spread':>7s} {'vs mean':>8s}")
print()
for _, x in t.iterrows():
    print(f"{x.model:11s} {x.dataset:17s} {x.target:6s} {x.n:5d} {x.mae:8.4f} "
          f"{x.r2:+7.3f} {x.bias:+8.3f} {x.spread:7.3f} {x.vs_mean_pct:+7.1f}%")

print()
print("spread is SD of predictions over SD of labels. near 1 means the model covers")
print("the range patients span, near 0 means it is close to a constant.")
print("vs mean is how much better than predicting the dataset average.")
print()
for name in ["EchoNet-Dynamic", "EchoNet-LVH", "MIMIC"]:
    g = t[t.dataset == name]
    if len(g):
        print(f"{name:17s}  spread {g.spread.mean():.2f}   vs mean {g.vs_mean_pct.mean():+.0f}%")
if len(t) > 3:
    print()
    print(f"across all {len(t)} cells, spread and vs-mean correlate at "
          f"{np.corrcoef(t.spread, t.vs_mean_pct)[0,1]:.2f}")

t.round(4).to_csv(OUT, index=False)
print()
print("saved to", OUT)
