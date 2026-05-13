#!/usr/bin/env bash
# install.sh — nazca-cohort-enrichment installer
# Usage: ./install.sh [--uninstall] [--yes]
#
# Options:
#   --yes        Skip all confirmation prompts
#   --uninstall  Remove the skill from ~/.claude/skills/ (data in ~/Factory/cohorts/ is never touched)

set -euo pipefail

SKILL_NAME="nazca-cohort-enrichment"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SKILLS_DIR="$CLAUDE_DIR/skills"
FACTORY_DIR="${NAZCA_FACTORY_DIR:-$HOME/Factory}"
COHORTS_DIR="$FACTORY_DIR/cohorts"

YES=false
UNINSTALL=false

for arg in "$@"; do
  case "$arg" in
    --yes) YES=true ;;
    --uninstall) UNINSTALL=true ;;
    *) echo "Unknown option: $arg" && exit 1 ;;
  esac
done

confirm() {
  if $YES; then return 0; fi
  read -r -p "$1 [y/N] " reply
  [[ "$reply" =~ ^[Yy]$ ]]
}

# ─── Uninstall ────────────────────────────────────────────────────────────────

if $UNINSTALL; then
  TARGET="$SKILLS_DIR/$SKILL_NAME"
  if [[ ! -d "$TARGET" ]]; then
    echo "Skill not found at $TARGET — nothing to remove."
    exit 0
  fi
  if confirm "Remove $TARGET?"; then
    rm -rf "$TARGET"
    echo "Removed $TARGET."
    echo "Note: $COHORTS_DIR was NOT touched — your pipeline data is safe."
  else
    echo "Aborted."
  fi
  exit 0
fi

# ─── Install ──────────────────────────────────────────────────────────────────

echo ""
echo "Installing $SKILL_NAME..."
echo "  Skills dir : $SKILLS_DIR"
echo "  Factory dir: $FACTORY_DIR"
echo ""

# Step 1 — copy skill
mkdir -p "$SKILLS_DIR"
TARGET="$SKILLS_DIR/$SKILL_NAME"
if [[ -d "$TARGET" ]]; then
  if confirm "Skill already exists at $TARGET. Overwrite?"; then
    rm -rf "$TARGET"
  else
    echo "Aborted."
    exit 1
  fi
fi
cp -R "$SCRIPT_DIR" "$TARGET"
echo "[1/4] Copied skill to $TARGET"

# Step 2 — create cohorts directory
mkdir -p "$COHORTS_DIR"
echo "[2/4] Created $COHORTS_DIR"

# Step 3 — initialize state
echo "[3/4] Initializing state..."
NAZCA_FACTORY_DIR="$FACTORY_DIR" python3 "$TARGET/scripts/cohort_manager.py" --setup

# Step 4 — check MCPs
echo "[4/4] Checking MCP configuration..."
MCP_CONFIG="$CLAUDE_DIR/claude_desktop_config.json"
WARN=false

if [[ -f "$MCP_CONFIG" ]]; then
  if ! grep -qi "edgar" "$MCP_CONFIG"; then
    echo "  WARNING: EDGAR MCP not found in $MCP_CONFIG"
    echo "           Public company enrichment requires edgartools — see https://github.com/dgunning/edgartools"
    WARN=true
  fi
  if ! grep -qi "harmonic" "$MCP_CONFIG"; then
    echo "  WARNING: Harmonic MCP not found in $MCP_CONFIG"
    echo "           Private company enrichment requires Harmonic — contact dan@nazca.vc"
    WARN=true
  fi
  if ! $WARN; then
    echo "  EDGAR and Harmonic MCPs detected."
  fi
else
  echo "  MCP config not found at $MCP_CONFIG — skipping MCP check."
  echo "  Ensure EDGAR and Harmonic MCPs are configured before running enrichment."
fi

# ─── Summary ──────────────────────────────────────────────────────────────────

echo ""
echo "Installation complete."
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code"
echo "  2. Start any session — the skill auto-triggers on enrichment/cohort tasks"
echo "  3. Optional: set NAZCA_FACTORY_DIR to override ~/Factory/"
echo ""
if [[ -n "${NAZCA_FACTORY_DIR_WAS_SET:-}" ]]; then
  echo "  State files: $COHORTS_DIR"
else
  echo "  State files: $COHORTS_DIR  (default; override with NAZCA_FACTORY_DIR env var)"
fi
echo ""
