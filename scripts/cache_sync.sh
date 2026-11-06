#!/usr/bin/env bash
#
# Sync pipeline-time artifacts to/from Cloudflare R2.
#
# The embedding cache (data/embedding_cache/) is a pipeline-time artifact: too
# large for git and never read by the deployed site, so it lives out-of-band in
# R2 instead. Re-embedding from scratch costs real OpenAI money, so back it up
# after any pipeline run that adds embeddings, and restore it on a fresh clone.
#
# Raw captures (data/*/raw_html/) are gitignored too, and for the no-Wayback
# companies (flock, bendingspoons) the local copies may be the only archival
# record anywhere — push-raw after every capture round.
#
#   ./scripts/cache_sync.sh push       # embedding cache: local -> R2
#   ./scripts/cache_sync.sh pull       # embedding cache: R2 -> local
#   ./scripts/cache_sync.sh push-raw   # raw_html dirs:   local -> R2
#   ./scripts/cache_sync.sh pull-raw   # raw_html dirs:   R2 -> local
#
# Requires an rclone remote named `cloudflare` (S3/Cloudflare provider) pointing
# at the `language-of-work` R2 bucket. `copy` never deletes, so a stray run can't
# wipe either side.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CACHE_REMOTE="cloudflare:language-of-work/embedding_cache"
CACHE_LOCAL="$ROOT/data/embedding_cache"
RAW_REMOTE="cloudflare:language-of-work/raw"
RAW_LOCAL="$ROOT/data"

case "${1:-}" in
  push) rclone copy --progress "$CACHE_LOCAL" "$CACHE_REMOTE" ;;
  pull) rclone copy --progress "$CACHE_REMOTE" "$CACHE_LOCAL" ;;
  push-raw) rclone copy --progress --include "*/raw_html/**" "$RAW_LOCAL" "$RAW_REMOTE" ;;
  pull-raw) rclone copy --progress --include "*/raw_html/**" "$RAW_REMOTE" "$RAW_LOCAL" ;;
  *) echo "usage: $0 {push|pull|push-raw|pull-raw}" >&2; exit 2 ;;
esac
