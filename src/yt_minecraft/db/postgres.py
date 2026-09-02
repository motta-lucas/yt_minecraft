def create_schema(cur, schema: str):

    schema_sql = f"CREATE SCHEMA IF NOT EXISTS {schema};"

    cur.execute(schema_sql)
