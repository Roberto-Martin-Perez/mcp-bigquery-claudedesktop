#!/bin/bash
set -e

echo "BigQuery MCP Server - Quick Install"
echo "===================================="
echo ""

# Get credentials path
CREDS="$1"
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
cat > claude_desktop_config.json << EOF
{
  "mcpServers": {
    "bigquery": {
      "command": "$PYTHON_PATH",
      "args": ["$SCRIPT_DIR/bigquery_mcp_server.py"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "$SCRIPT_DIR/credentials.json",
        "BIGQUERY_PROJECT": "your-project-id",
        "BIGQUERY_ADDITIONAL_PROJECTS": ""
      }
    }
  }
}
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Installation complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo ""
echo "1. Edit claude_desktop_config.json"
echo "   Set BIGQUERY_PROJECT to your project ID"
echo ""
echo "2. Copy config to Claude Desktop:"
echo "   cp claude_desktop_config.json ~/Library/Application\\ Support/Claude/"
echo ""
echo "3. Restart Claude Desktop (Cmd+Q)"
echo ""
