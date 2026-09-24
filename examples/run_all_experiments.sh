#!/bin/bash
# Parallel experiment driver: all six arms concurrently, outputs to /tmp.
cd /tmp/jev-quilt
mkdir -p /tmp/exp-logs
for e in witness_rng gan opponent changepoint brew opposites; do
  python3 examples/exp_$e.py > /tmp/exp-logs/$e.log 2>&1 &
done
wait
for e in witness_rng gan opponent changepoint brew opposites; do
  echo "----- $e"
  cat /tmp/exp-logs/$e.log
done
