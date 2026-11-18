#!/bin/zsh
# Run one heavy job at a time on this 16 GB laptop: a render, model inference on clips, a long encode.
#   video/tools/heavy.sh <command> [args...]
# The shared lock is the guard: only one heavy job runs at a time. Before starting, it also waits (at most MAX_WAIT
# seconds, default 180) for memory to be free (MIN_FREE %, default 25) and for the 1-minute load to fall below MAX_LOAD
# (default 3 x the CPU count); after that it runs anyway, because background work such as Spotlight indexing can keep
# the load high for a long time without any danger. The job runs at low priority.
# On 18 Nov 2026 two renders, the detector, the camera service and encodes ran at once and the Mac stopped with a
# watchdog panic. Remotion renders started through this should also pass --concurrency=2.
emulate -L zsh
set -u
LOCK=/private/tmp/claude-501/heavy.lock
MAX_LOAD=${MAX_LOAD:-$(( $(sysctl -n hw.ncpu) * 3 ))}
MIN_FREE=${MIN_FREE:-25}
MAX_WAIT=${MAX_WAIT:-180}
mkdir -p /private/tmp/claude-501
until mkdir "$LOCK" 2>/dev/null; do
  # a lock left by a process that no longer exists is stale
  holder=$(cat "$LOCK/pid" 2>/dev/null || true)
  if [[ -n "$holder" ]] && ! kill -0 "$holder" 2>/dev/null; then rm -rf "$LOCK"; continue; fi
  sleep 5
done
echo $$ > "$LOCK/pid"
trap 'rm -rf "$LOCK"' EXIT INT TERM
waited=0
while (( waited < MAX_WAIT )); do
  load=$(sysctl -n vm.loadavg | awk '{print int($2)}')
  free=$(memory_pressure -Q 2>/dev/null | awk -F': ' '/free percentage/ {gsub("%","",$2); print int($2)}')
  (( load < MAX_LOAD && ${free:-100} >= MIN_FREE )) && break
  echo "heavy.sh: load $load (max $MAX_LOAD), memory free ${free:-?} % (min $MIN_FREE), waiting" >&2
  sleep 15; (( waited += 15 ))
done
nice -n 10 "$@"
