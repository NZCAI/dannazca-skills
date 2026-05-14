#!/usr/bin/env bash
# install.sh — nazca-private-scoring installer
# Usage: ./install.sh [--uninstall] [--yes]
#
# Options:
#   --yes        Skip all confirmation prompts
#   --uninstall  Remove skill from ~/.claude/skills/ (data in ~/Factory/ is never touched)

set -euo pipefail

SKILL_NAME="nazca-private-scoring"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SKILLS_DIR="$CLAUDE_DIR/skills"
FACTORY_DIR="${NAZCA_FACTORY_DIR:-$HOME/Factory}"
SCORING_DIR="$FACTORY_DIR/private-scoring"

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
    echo "Note: $SCORING_DIR was NOT touched — your pipeline data is safe."
  else
    echo "Aborted."
  fi
  exit 0
fi

# ─── Install ──────────────────────────────────────────────────────────────────

echo ""
echo "Installing $SKILL_NAME..."
echo "  Skills dir  : $SKILLS_DIR"
echo "  Pipeline dir: $SCORING_DIR"
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

# Step 2 — create pipeline directories
mkdir -p "$SCORING_DIR/inputs" "$SCORING_DIR/scores"
echo "[2/4] Created $SCORING_DIR/"

# Step 3 — initialize state + placeholder templates
echo "[3/4] Initializing pipeline state..."
NAZCA_FACTORY_DIR="$FACTORY_DIR" python3 "$TARGET/scripts/private_score_manager.py" --setup

# Step 4 — check MCPs
echo "[4/4] Checking MCP configuration..."
MCP_CONFIG="$CLAUDE_DIR/claude_desktop_config.json"
WARN=false

if [[ -f "$MCP_CONFIG" ]]; then
  if ! grep -qi "harmonic" "$MCP_CONFIG"; then
    echo "  WARNING: Harmonic MCP not found in $MCP_CONFIG"
    echo "           Private company traction data requires Harmonic — contact dan@nazca.vc"
    WARN=true
  fi
  if ! grep -qi "edgar" "$MCP_CONFIG"; then
    echo "  WARNING: EDGAR MCP not found in $MCP_CONFIG"
    echo "           Sector growth and liquidity data requires edgartools"
    WARN=true
  fi
  if ! $WARN; then
    echo "  Harmonic and EDGAR MCPs detected."
  fi
else
  echo "  MCP config not found at $MCP_CONFIG — skipping MCP check."
  echo "  Ensure Harmonic and EDGAR MCPs are configured before running scoring."
fi

# ─── Summary ──────────────────────────────────────────────────────────────────

echo ""
echo "Installation complete."
echo ""
echo "Next steps:"
echo "  1. Fill in your company data:"
echo "     open \"$SCORING_DIR/inputs/company_inputs.json\""
echo "     (paste Pitchbook/Crunchbase exports here)"
echo ""
echo "  2. Restart Claude Code"
echo ""
echo "  3. Start a session — the skill auto-triggers on private company scoring tasks"
echo ""
echo "  Data directory: $SCORING_DIR"
echo "  EDGAR MCP: sector growth + liquidity (no daily limit)"
echo "  Harmonic MCP: headcount, growth, pedigree (10 calls/day = 5 companies/day)"
echo ""
