"""
probed <csv> <out> <label> <unit> <mean> <std>
zs <csv> <out> <label> <unit>
"""
import sys, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
mode = sys.argv[1]
if mode == "probed":
	csv, out, label, unit = sys.argv[2:6]
	mean, std = float(sys.argv[6]), float(sys.argv[7])
	df = pd.read_csv(csv)
	y = (df["label_real"].values - mean) / std
	p = (df["pred_real"].values - mean) / std
	colour, tag = "#1f4e9c", "probed"
else:
	csv, out, label, unit = sys.argv[2:6]
	df = pd.read_csv(csv)
	y, p = df["label"].values, df["pred"].values
	colour, tag = "#8c3b2f", "zero-shot"
mae = np.mean(np.abs(y - p))
r2 = 1 - np.sum((y-p)**2) / np.sum((y - y.mean())**2)
bias = np.mean(p - y)
mae_mean = np.mean(np.abs(y - y.mean())) # what predicting the mean would give
fig, ax = plt.subplots(figsize=(6,6))
ax.scatter(y, p, s=9, alpha=.5, color=colour,label=f"{tag} MAE = {mae:.3f} {unit} $R^2$ = {r2:.3f}")
m = 0.06*(max(y.max(),p.max()) - min(y.min(),p.min()))
lo, hi = min(y.min(),p.min())-m, max(y.max(),p.max())+m
ax.plot([lo,hi],[lo,hi], ":", color="grey", lw=1.2, label="identity")
ax.axhline(y.mean(), color="green", ls="--", lw=1.0, alpha=.6,label=f"predict-the-mean (MAE {mae_mean:.3f})")
ax.set_xlim(lo,hi); ax.set_ylim(lo,hi); ax.set_aspect("equal")
ax.set_xlabel(f"Ground truth {label} ({unit})")
ax.set_ylabel(f"Predicted {label} ({unit})")
ax.set_title(f"PanEcho {tag}: {label} (n={len(df)})")
ax.legend(loc="upper left", fontsize=8); ax.grid(alpha=.3)
plt.tight_layout(); plt.savefig(out, dpi=150)
print(f"{out}\n n={len(df)} MAE={mae:.4f} {unit} R2={r2:.4f} "f"bias={bias:+.4f} predict-mean MAE={mae_mean:.4f}")
