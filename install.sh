#!/usr/bin/env bash
# Install as a Claude Code skill: ./install.sh   (or clone straight into ~/.claude/skills/sko_2027)
set -e
DEST="$HOME/.claude/skills/sko_2027"
HERE="$(cd "$(dirname "$0")" && pwd)"
if [ "$HERE" = "$DEST" ]; then echo "Already in place: $DEST"; exit 0; fi
mkdir -p "$HOME/.claude/skills"
rm -rf "$DEST"; cp -R "$HERE" "$DEST"; rm -rf "$DEST/.git"
[ -f "$DEST/spec.json" ] || cp "$DEST/spec.example.json" "$DEST/spec.json"
echo "Installed to $DEST"
echo "Next: python3 $DEST/server.py   (opens the spec form at http://localhost:7894)"
