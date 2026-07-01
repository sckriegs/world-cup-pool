#!/usr/bin/env bash
# Run this in the Replit Shell when a git pull has merge conflicts.
# Discards local Replit edits and matches GitHub main exactly.
set -euo pipefail

git merge --abort 2>/dev/null || true
git fetch origin
git reset --hard origin/main
git clean -fd --exclude=.replit --exclude=replit.nix

echo "Done. Workspace now matches origin/main."
echo "Next: republish your Replit deployment, then hard-refresh the Leaderboard."
