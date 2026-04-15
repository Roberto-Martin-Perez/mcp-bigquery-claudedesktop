# BigQuery MCP Server for Claude Desktop

Connect Claude Desktop to Google BigQuery. Query your data with natural language instead of SQL.

## Quick Start

### Requirements

- [Claude Desktop](https://claude.ai/download)
- Python 3.11+
- Google Cloud BigQuery credentials (JSON file)

### Installation

```bash
# 1. Clone
git clone <this-repo>
cd mcp-bigquery-claude

# 2. Install
./install.sh --credentials /path/to/your-credentials.json

# 3. Restart Claude Desktop
# Press Cmd+Q and reopen

# 4. Test
# In Claude Desktop: "List all BigQuery projects"
```

## Manual Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy your credentials
cp /path/to/credentials.json credentials.json

# 3. Configure Claude Desktop
# Edit the paths in claude_desktop_config.json to match your setup
# Then copy:
cp claude_desktop_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 4. Restart Claude Desktop
```

## Configuration

Edit `bigquery_mcp_server.py` lines 14-16:

```python
PROJECT_ID = "your-billing-project"
CREDENTIALS_PATH = "credentials.json"
```

For cross-project queries, the billing project needs `bigquery.jobs.create` permission.
Data projects only need `bigquery.dataViewer` permission.

## Usage Examples

In Claude Desktop:

```
List all my BigQuery projects

Show me tables in dataset analytics

Get schema of table users

How many records are in table events?

Execute: SELECT COUNT(*) FROM `project.dataset.table`
```

## Available Tools

- `list_projects` - List configured projects
- `list_datasets` - List datasets
- `list_tables` - List tables in a dataset
- `get_table_schema` - Get table schema
- `run_query` - Execute SQL (read-only, max 100 rows)
- `get_table_preview` - Preview table data

## Troubleshooting

### MCP not showing in Claude Desktop

```bash
# Check config
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Check logs
# Open Claude Desktop → Cmd+Shift+D
```

### Permission errors

- Ensure `BIGQUERY_PROJECT` in config is your billing project (where you have `bigquery.jobs.create`)
- Your credentials need `BigQuery Job User` + `BigQuery Data Viewer` roles

### Test connection

```bash
python3 test_connection.py
```

## Security

- Read-only access
- Queries limited to 100 rows
- Credentials never committed (see `.gitignore`)

## License

MIT
