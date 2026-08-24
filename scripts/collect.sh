#!/bin/bash
# Pull every artefact out of the run directories into results/.
# Never touches .pt files. Safe to rerun after any run finishes.
source /home/abag/REPRODUCED/paths.sh
cd $REPO
mkdir -p results/{logs,epoch_logs,preds,figs,curves}
cp -n $RUNS/*.log results/logs/ 2>/dev/null
cp -n $RUNS/preds/*.csv results/preds/ 2>/dev/null
cp -n $RUNS/figs/probed_*.png results/figs/ 2>/dev/null
cp -n $RUNS/figs/zs_*.png results/figs/ 2>/dev/null
cp -n $RUNS/figs/curve_*.png results/curves/ 2>/dev/null
for d in $RUNS/*/video_classification_frozen/*/; do
tag=$(basename "$d")
[ -f "$d/log_r0.csv" ] && cp "$d/log_r0.csv" "results/epoch_logs/${tag}.csv"
done
echo "logs echo "preds echo "figs echo "curves $(ls results/logs 2>/dev/null | wc -l)"
echo "epoch_logs $(ls results/epoch_logs 2>/dev/null | wc -l)"
$(ls results/preds 2>/dev/null | wc -l)"
echo "logs       $(ls results/logs 2>/dev/null | wc -l)"
echo "epoch_logs $(ls results/epoch_logs 2>/dev/null | wc -l)"
echo "preds      $(ls results/preds 2>/dev/null | wc -l)"
echo "figs       $(ls results/figs 2>/dev/null | wc -l)"
echo "curves     $(ls results/curves 2>/dev/null | wc -l)"
