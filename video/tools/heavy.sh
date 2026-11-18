#!/bin/zsh
# Run one heavy job at a time on this 16 GB laptop: a render, model inference on clips, a long encode.
#   video/tools/heavy.sh <command> [args...]
# Waits for the shared lock and for the 1-minute load average to fall below MAX_LOAD (default 8), runs the command at
# low priority, then releases the lock. On 18 Nov 2026 two renders, the detector, the camera service and encodes ran
# at once and the Mac stopped with a watchdog panic; this is the guard against that.
# Remotion renders started through it should also pass --concurrency=2.
emulate -L zsh
set -u
LOCK=/private/tmp/claude-501/heavy.lock
MAX_LOAD=${MAX_LOAD:-8}
mkdir -p /private/tmp/claude-501
until mkdir "$LOCK" 2>/dev/null; do
  # a lock left by a process that no longer exists is stale
  holder=$(cat "$LOCK/pid" 2>/dev/null || true)
  if [[ -n "$holder" ]] && ! kill -0 "$holder" 2>/dev/null; then rm -rf "$LOCK"; continue; fi
  sleep 5
done
echo $$ > "$LOCK/pid"
trap 'rm -rf "$LOCK"' EXIT INT TERM
while :; do
  load=$(sysctl -n vm.loadavg | awk '{print int($2)}')
  (( load < MAX_LOAD )) && break
  echo "heavy.sh: load $load ≥ $MAX_LOAD, waiting" >&2
  sleep 15
done
nice -n 10 "$@"
