"""plot_curve.py <log_r0.csv> <out.png> <std> <unit> <title>"""
import sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
csv, out, std, unit, title = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4], sys.argv[5]
ep, tr, va = [], [], []
for line in open(csv):
	p = line.strip().split(",")
	if len(p) != 3 or not p[0].isdigit(): continue
	e = int(p[0])
	if e in ep: continue
	ep.append(e); tr.append(float(p[1])/std); va.append(float(p[2])/std)
best = [min(va[:i+1]) for i in range(len(va))]
fig, ax = plt.subplots(1, 2, figsize=(12,4.5))
ax[0].plot(ep, tr, "o-", lw=1.8, ms=4, label="train")
ax[0].plot(ep, va, "o-", lw=1.8, ms=4, label="val")
ax[0].plot(ep, best, "--", lw=1.3, color="grey", label="best val so far")
ax[0].set_xlabel("epoch"); ax[0].set_ylabel(f"MAE ({unit})")
ax[0].set_title(title); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)
ax[1].plot(ep, va, "o-", lw=1.8, ms=4, color="#c1512f", label="val")
ax[1].plot(ep, best, "--", lw=1.3, color="grey", label="best val so far")
ax[1].set_xlabel("epoch"); ax[1].set_ylabel(f"val MAE ({unit})")
ax[1].set_title("Validation only"); ax[1].legend(fontsize=8); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig(out, dpi=150)
print(f"{out}\n best val {min(va):.4f} {unit} @ epoch {ep[va.index(min(va))]}"
f" final train {tr[-1]:.4f} final val {va[-1]:.4f}")
