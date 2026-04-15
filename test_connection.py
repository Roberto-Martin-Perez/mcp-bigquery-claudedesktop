#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión a BigQuery
"""

from google.cloud import bigquery
from google.oauth2 import service_account

CREDENTIALS_PATH = "credentials.json"
PROJECT_ID = "your-project-id"

print("=" * 60)
print("  Verificación de conexión a BigQuery")
print("=" * 60)
print()

try:
    print(f"📡 Conectando al proyecto: {PROJECT_ID}")
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=["https://www.googleapis.com/auth/bigquery.readonly"],
    )
    client = bigquery.Client(project=PROJECT_ID, credentials=credentials)

    print("✅ Credenciales cargadas correctamente")
    print()

    print("📊 Listando datasets...")
    datasets = list(client.list_datasets())

    if not datasets:
        print("⚠️  No se encontraron datasets en este proyecto")
    else:
        print(f"✅ Se encontraron {len(datasets)} dataset(s):")
        print()

        for ds in datasets:
            print(f"  Dataset: {ds.dataset_id}")
            tables = list(client.list_tables(ds.dataset_id))
            print(f"  └─ Tablas: {len(tables)}")

            for table in tables[:3]:
                print(f"     • {table.table_id}")

            if len(tables) > 3:
                print(f"     ... y {len(tables) - 3} más")
            print()

    print("=" * 60)
    print("🎉 ¡Conexión exitosa!")
    print("=" * 60)
    print()
    print("Ahora puedes:")
    print("  1. Configurar el MCP server siguiendo QUICKSTART.md")
    print("  2. O usar el script: python ask_bigquery.py")
    print()

except Exception as e:
    print()
    print("=" * 60)
    print("❌ Error de conexión")
    print("=" * 60)
    print()
    print(f"Error: {e}")
    print()
    print("Verifica que:")
    print("  • El archivo credentials.json existe")
    print("  • Tienes permisos de BigQuery en el proyecto")
    print("  • El PROJECT_ID está configurado correctamente")
    print()
    import sys
    sys.exit(1)
