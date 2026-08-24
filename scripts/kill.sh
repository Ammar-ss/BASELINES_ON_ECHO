#!/bin/bash
source /home/abag/REPRODUCED/paths.sh
echo "your evals.main processes:"
ps -u $USER -o pid,etime,cmd | grep "[e]vals.main" || { echo "none"; exit 0; }
read -p "kill all of the above? [y/N] " ok
[ "$ok" = "y" ] || exit 0
pkill -u $USER -f evals.main
sleep 3
nvidia-smi --query-gpu=index,memory.used --format=csv
