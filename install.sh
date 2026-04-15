#!/bin/bash
set -e

echo "BigQuery MCP Server - Quick Install"
echo "===================================="
echo ""

# Parse arguments
CREDS=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --credentials)
            CREDS="$2"
            shift 2
            ;;
        *)
            # If no flag, assume it's the credentials path
            CREDS="$1"
            shift
            ;;
    esac
done

# If still empty, ask interactively
if [ -z "$CREDS" ]; then
    read -p "Path to credentials.json: " CREDS
fi

if [ ! -f "$CREDS" ]; then
    echo "❌ File not found: $CREDS"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Copy credentials
cp "$CREDS" credentials.json
echo "✅ Credentials copied"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install --user -q -r requirements.txt
echo "✅ Dependencies installed"

# Get Python path
PYTHON_PATH=$(which python3)

# Create config
CONFIG_FILE="$SCRIPT_DIR/claude_desktop_config.json"
cat > "$CONFIG_FILE" << 'EOF'
{
  "mcpServers": {
    "bigquery": {
      "command": "PYTHON_PATH_PLACEHOLDER",
      "args": ["SCRIPT_DIR_PLACEHOLDER/bigquery_mcp_server.py"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "SCRIPT_DIR_PLACEHOLDER/credentials.json",
        "BIGQUERY_PROJECT": "your-project-id",
        "BIGQUERY_ADDITIONAL_PROJECTS": ""
      }
    }
  }
}
EOF

# Replace placeholders (works on both macOS and Linux)
sed -i.backup "s|PYTHON_PATH_PLACEHOLDER|$PYTHON_PATH|g" "$CONFIG_FILE"
sed -i.backup "s|SCRIPT_DIR_PLACEHOLDER|$SCRIPT_DIR|g" "$CONFIG_FILE"
rm -f "$CONFIG_FILE.backup"

if [ -f "$CONFIG_FILE" ]; then
    echo "✅ Configuration file created: $CONFIG_FILE"
else
    echo "❌ Failed to create configuration file"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Installation complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit $CONFIG_FILE"
echo "   Set BIGQUERY_PROJECT to your project ID"
echo ""
echo "2. Copy config to Claude Desktop:"
echo "   cp $CONFIG_FILE ~/Library/Application\\ Support/Claude/"
echo ""
echo "3. Restart Claude Desktop (Cmd+Q)"
echo ""
