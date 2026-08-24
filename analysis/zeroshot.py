import sys, os, argparse, numpy as np, pandas as pd, torch
import torch.nn.functional as F

sys.path.insert(0, "/home/abag/baselines/EchoJEPA/evals/video_classification_frozen/modelcustom/PanEcho")
import hubconf

ap = argparse.ArgumentParser()
ap.add_argument("--task", required=True)          # EF, LVIDd, IVSd, LVPWd, LVIDs, RVSP
ap.add_argument("--csv", required=True)           # test CSV, "path label" per line
ap.add_argument("--out", required=True)
ap.add_argument("--device", default="cuda:0")
ap.add_argument("--frames", type=int, default=16)
ap.add_argument("--step", type=int, default=2)
a = ap.parse_args()

import cv2
dev = a.device if torch.cuda.is_available() else "cpu"
model = hubconf.PanEcho(pretrained=True, clip_len=a.frames, tasks=[a.task]).to(dev).eval()

def load_clip(path):
    cap = cv2.VideoCapture(path)
    frames = []
    while True:
        ok, fr = cap.read()
        if not ok: break
        frames.append(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
    cap.release()
    if not frames: return None
    need = (a.frames - 1) * a.step + 1
    while len(frames) < need:
        frames = frames + frames                       # loop short clips
    start = (len(frames) - need) // 2                  # centre crop in time
    idx = [start + i * a.step for i in range(a.frames)]
    clip = np.stack([frames[i] for i in idx])          # T,H,W,C
    t = torch.from_numpy(clip).float().div(255.)
    t = t.permute(3, 0, 1, 2).unsqueeze(0)             # 1,C,T,H,W
    t = F.interpolate(t.squeeze(0).permute(1,0,2,3), size=(224,224),
                      mode="bilinear", align_corners=False)
    return t.permute(1,0,2,3).unsqueeze(0)

rows = [l.rsplit(" ", 1) for l in open(a.csv).read().strip().split("\n")]
preds, labels, paths, fails = [], [], [], 0

with torch.no_grad():
    for i, (p, lab) in enumerate(rows):
        clip = load_clip(p)
        if clip is None:
            fails += 1; continue
        out = model(clip.to(dev))
        preds.append(float(out[a.task].squeeze().cpu()))
        labels.append(float(lab)); paths.append(p)
        if i % 200 == 0: print(f"{i}/{len(rows)}", flush=True)

df = pd.DataFrame({"video_path": paths, "label": labels, "pred": preds})
df["abs_error"] = (df.label - df.pred).abs()
os.makedirs(os.path.dirname(a.out), exist_ok=True)
df.to_csv(a.out, index=False)

mae = df.abs_error.mean()
r2 = 1 - ((df.label-df.pred)**2).sum() / ((df.label-df.label.mean())**2).sum()
print(f"\ntask={a.task}  n={len(df)}  failed={fails}")
print(f"MAE={mae:.4f}  R2={r2:.4f}")
