#!/usr/bin/env bash
#
# Sync the embedding cache to/from Cloudflare R2.
#
# The embedding cache (data/embedding_cache/) is a pipeline-time artifact: too
# large for git and never read by the deployed site, so it lives out-of-band in
# R2 instead. Re-embedding from scratch costs real OpenAI money, so back it up
# after any pipeline run that adds embeddings, and restore it on a fresh clone.
#
#   ./scripts/cache_sync.sh push   # local -> R2 (after adding embeddings)
#   ./scripts/cache_sync.sh pull   # R2 -> local (on a fresh clone)
#
# Requires an rclone remote named `cloudflare` (S3/Cloudflare provider) pointing
# at the `language-of-work` R2 bucket. `copy` never deletes, so a stray run can't
# wipe either side.
set -euo pipefail

REMOTE="cloudflare:language-of-work/embedding_cache"
LOCAL="$(cd "$(dirname "$0")/.." && pwd)/data/embedding_cache"

case "${1:-}" in
  push) rclone copy --progress "$LOCAL" "$REMOTE" ;;
  pull) rclone copy --progress "$REMOTE" "$LOCAL" ;;
  *) echo "usage: $0 {push|pull}" >&2; exit 2 ;;
esac
