def ensure_raw_table(cur, table_name: str, key_column: str):

    cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS raw.{table_name} (
                        id SERIAL PRIMARY KEY,
                        data JSONB NOT NULL,
                        _extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """)
    cur.execute(f"ALTER TABLE raw.{table_name} ADD COLUMN IF NOT EXISTS {key_column} TEXT;")

    cur.execute(f"""
                    CREATE INDEX IF NOT EXISTS ix_raw_{table_name}_extracted_at
                    ON raw.{table_name} (_extracted_at);
        """)

    cur.execute(f"""
                    CREATE INDEX IF NOT EXISTS ix_raw_{table_name}_{key_column}
                    ON raw.{table_name} ({key_column});
        """)

    cur.execute(f"""
                    CREATE INDEX IF NOT EXISTS ix_raw_{table_name}_{key_column}_extracted_at
                    ON raw.{table_name} ({key_column}, _extracted_at);
        """)
