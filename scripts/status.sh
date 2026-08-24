#!/bin/bash
source /home/abag/REPRODUCED/paths.sh
CFG=$1
echo "=== tmux sessions ==="
tmux ls 2>/dev/null || echo "none"
echo
echo "=== my GPU processes ==="
nvidia-smi | grep "envs/$CONDA_ENV" || echo "none"
echo
if [ -n "$CFG" ]; then
echo "=== epochs: $CFG ==="
grep "val(min-head)" $REPO/results/logs/${CFG}.log 2>/dev/null | awk '!seen[$0]++' | echo
echo "=== latest line ==="
tail -1 $REPO/results/logs/${CFG}.log 2>/dev/null
tail -
fi
