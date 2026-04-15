#!/usr/bin/env python3
"""
BigQuery MCP Server - Servidor MCP para acceder a BigQuery desde Claude Desktop
"""

import os
import json
import asyncio
from typing import Any
from datetime import date, datetime, time
from decimal import Decimal
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from google.cloud import bigquery
from google.oauth2 import service_account

# Configuración
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
DEFAULT_PROJECT = os.getenv("BIGQUERY_PROJECT", "your-billing-project-id")
ADDITIONAL_PROJECTS = os.getenv("BIGQUERY_ADDITIONAL_PROJECTS", "").split(",")

# Cliente de BigQuery global
bq_client = None


def serialize_bigquery_value(value):
    """Convierte tipos de BigQuery a tipos serializables JSON."""
    if value is None:
        return None
    elif isinstance(value, (date, datetime)):
        return value.isoformat()
    elif isinstance(value, time):
        return value.isoformat()
    elif isinstance(value, Decimal):
        return float(value)
    elif isinstance(value, bytes):
        return value.decode('utf-8', errors='ignore')
    else:
        return value


def get_bigquery_client(project_id=None):
    """Obtiene o crea el cliente de BigQuery."""
    global bq_client

    if project_id is None:
        project_id = DEFAULT_PROJECT

    if os.path.exists(CREDENTIALS_PATH):
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_PATH,
            scopes=["https://www.googleapis.com/auth/bigquery"],
        )
        return bigquery.Client(project=project_id, credentials=credentials)
    else:
        return bigquery.Client(project=project_id)


# Crear servidor MCP
app = Server("bigquery-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Lista todas las herramientas disponibles."""
    return [
        Tool(
            name="list_projects",
            description="Lista todos los proyectos de BigQuery configurados",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="list_datasets",
            description="Lista todos los datasets de un proyecto de BigQuery",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": f"ID del proyecto (default: {DEFAULT_PROJECT})",
                    }
                },
            },
        ),
        Tool(
            name="list_tables",
            description="Lista todas las tablas de un dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "ID del dataset",
                    },
                    "project_id": {
                        "type": "string",
                        "description": f"ID del proyecto (default: {DEFAULT_PROJECT})",
                    },
                },
                "required": ["dataset_id"],
            },
        ),
        Tool(
            name="get_table_schema",
            description="Obtiene el esquema completo de una tabla (columnas, tipos, descripciones)",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "ID del dataset",
                    },
                    "table_id": {
                        "type": "string",
                        "description": "ID de la tabla",
                    },
                    "project_id": {
                        "type": "string",
                        "description": f"ID del proyecto (default: {DEFAULT_PROJECT})",
                    },
                },
                "required": ["dataset_id", "table_id"],
            },
        ),
        Tool(
            name="run_query",
            description="Ejecuta una query SQL en BigQuery (solo lectura, limitado a 100 filas)",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "Query SQL a ejecutar",
                    },
                    "project_id": {
                        "type": "string",
                        "description": f"ID del proyecto (default: {DEFAULT_PROJECT})",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Número máximo de filas a devolver (default: 50, max: 100)",
                    },
                },
                "required": ["sql"],
            },
        ),
        Tool(
            name="get_table_preview",
            description="Obtiene una vista previa de los datos de una tabla (primeras filas)",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "ID del dataset",
                    },
                    "table_id": {
                        "type": "string",
                        "description": "ID de la tabla",
                    },
                    "project_id": {
                        "type": "string",
                        "description": f"ID del proyecto (default: {DEFAULT_PROJECT})",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Número de filas a mostrar (default: 10, max: 50)",
                    },
                },
                "required": ["dataset_id", "table_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Maneja las llamadas a las herramientas."""

    try:
        if name == "list_projects":
            projects = [DEFAULT_PROJECT] + [p.strip() for p in ADDITIONAL_PROJECTS if p.strip()]
            result = {
                "projects": projects,
                "default": DEFAULT_PROJECT,
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "list_datasets":
            project_id = arguments.get("project_id", DEFAULT_PROJECT)
            client = get_bigquery_client(project_id)
            datasets = list(client.list_datasets())
            dataset_list = [ds.dataset_id for ds in datasets]
            result = {
                "project": project_id,
                "datasets": dataset_list,
                "count": len(dataset_list),
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "list_tables":
            project_id = arguments.get("project_id", DEFAULT_PROJECT)
            dataset_id = arguments["dataset_id"]
            client = get_bigquery_client(project_id)
            tables = list(client.list_tables(dataset_id))
            table_list = [t.table_id for t in tables]
            result = {
                "project": project_id,
                "dataset": dataset_id,
                "tables": table_list,
                "count": len(table_list),
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_table_schema":
            project_id = arguments.get("project_id", DEFAULT_PROJECT)
            dataset_id = arguments["dataset_id"]
            table_id = arguments["table_id"]
            client = get_bigquery_client(project_id)

            table_ref = f"{project_id}.{dataset_id}.{table_id}"
            table = client.get_table(table_ref)

            schema = []
            for field in table.schema:
                schema.append({
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode,
                    "description": field.description or "",
                })

            result = {
                "table": table_ref,
                "num_rows": table.num_rows,
                "size_mb": round(table.num_bytes / 1024 / 1024, 2),
                "created": table.created.isoformat() if table.created else None,
                "modified": table.modified.isoformat() if table.modified else None,
                "schema": schema,
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

        elif name == "run_query":
            # IMPORTANTE: Siempre usar DEFAULT_PROJECT como billing project
            # Esto permite ejecutar queries cross-project sin problemas de permisos
            sql = arguments["sql"]
            limit = min(arguments.get("limit", 50), 100)

            # IMPORTANTE: Siempre usar DEFAULT_PROJECT como billing project
            # Las queries pueden acceder a datos de otros proyectos usando fully-qualified table names
            client = get_bigquery_client(DEFAULT_PROJECT)
            query_job = client.query(sql)
            results = query_job.result()

            rows = []
            for row in results:
                # Serializar cada valor de la fila
                serialized_row = {key: serialize_bigquery_value(value) for key, value in dict(row).items()}
                rows.append(serialized_row)
                if len(rows) >= limit:
                    break

            result = {
                "billing_project": DEFAULT_PROJECT,
                "sql": sql,
                "rows_returned": len(rows),
                "total_rows": results.total_rows,
                "data": rows,
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

        elif name == "get_table_preview":
            # El proyecto puede ser diferente al billing project
            target_project = arguments.get("project_id", DEFAULT_PROJECT)
            dataset_id = arguments["dataset_id"]
            table_id = arguments["table_id"]
            limit = min(arguments.get("limit", 10), 50)

            # Usar fully-qualified table name para cross-project access
            sql = f"SELECT * FROM `{target_project}.{dataset_id}.{table_id}` LIMIT {limit}"

            # IMPORTANTE: Siempre usar DEFAULT_PROJECT como billing project
            client = get_bigquery_client(DEFAULT_PROJECT)
            query_job = client.query(sql)
            results = query_job.result()

            rows = []
            for row in results:
                # Serializar cada valor de la fila
                serialized_row = {key: serialize_bigquery_value(value) for key, value in dict(row).items()}
                rows.append(serialized_row)

            result = {
                "table": f"{target_project}.{dataset_id}.{table_id}",
                "billing_project": DEFAULT_PROJECT,
                "preview_rows": len(rows),
                "data": rows,
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

        else:
            return [TextContent(type="text", text=f"Error: herramienta desconocida '{name}'")]

    except Exception as e:
        error_msg = {
            "error": str(e),
            "tool": name,
            "arguments": arguments,
        }
        return [TextContent(type="text", text=json.dumps(error_msg, indent=2))]


async def main():
    """Punto de entrada del servidor MCP."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
