#!/bin/bash
# usage: ./scripts/run.sh <config_name> [n_gpus]
set -e
source /home/abag/REPRODUCED/paths.sh
CFG=$1
NGPU=${2:-4}
if [ -z "$CFG" ]; then
echo "usage: ./scripts/run.sh <config_name> [n_gpus]"
echo
echo "available configs:"
ls $REPO/configs/*.yaml 2>/dev/null | xargs -n1 basename | sed 's/.yaml//' | sed 's/^/ /'
exit 1
fi
CFGPATH=$REPO/configs/$CFG.yaml
[ -f "$CFGPATH" ] || { echo "no such config: $CFGPATH"; exit 1; }
FREE=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits \
| awk -F', ' '$2 < 1000 {print $1}' | head -n $NGPU)
COUNT=$(echo "$FREE" | wc -w)
if [ "$COUNT" -eq 0 ]; then
echo "no free GPUs"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv
exit 1
fi
if [ "$COUNT" -lt "$NGPU" ]; then
echo "only $COUNT free GPUs (wanted $NGPU)"
read -p "continue with $COUNT? [y/N] " ok
[ "$ok" = "y" ] || exit 1
fi
DEVICES=$(echo $FREE | tr ' ' '\n' | sed 's/^/cuda:/' | tr '\n' ' ')
LOG=$REPO/results/logs/${CFG}.log
echo "config : $CFG"
echo "devices: $DEVICES (world size $COUNT)"
echo "log : $LOG"
tmux kill-session -t $CFG 2>/dev/null || true
tmux new-session -d -s $CFG \
"source ~/miniconda3/etc/profile.d/conda.sh && conda activate $CONDA_ENV && \
cd $ENGINE && python -m evals.main --fname $CFGPATH --devices $DEVICES 2>&1 | tee -a $LOG"
sleep 3
echo
echo "launched in tmux session: $CFG"
echo " watch tmux attach -t $CFG (detach: Ctrl+B then d)"
echo " status ./scripts/status.sh $CFG"
