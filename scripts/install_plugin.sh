#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${IMAGEN_DESIGN_HUB_REPO:-https://github.com/Tygb99/imagen-design-hub.git}"
PLUGIN_DIR="${IMAGEN_DESIGN_HUB_PLUGIN_DIR:-$HOME/plugins/imagen-design-hub}"

if ! command -v git >/dev/null 2>&1; then
  echo "git is required." >&2
  exit 1
fi

if ! command -v node >/dev/null 2>&1; then
  echo "node is required." >&2
  exit 1
fi

if [ -d "$PLUGIN_DIR/.git" ]; then
  git -C "$PLUGIN_DIR" pull --ff-only
elif [ -e "$PLUGIN_DIR" ]; then
  echo "$PLUGIN_DIR exists but is not a git checkout. Move it away or set IMAGEN_DESIGN_HUB_PLUGIN_DIR." >&2
  exit 1
else
  mkdir -p "$(dirname "$PLUGIN_DIR")"
  git clone "$REPO_URL" "$PLUGIN_DIR"
fi

node "$PLUGIN_DIR/scripts/register_marketplace.mjs"
