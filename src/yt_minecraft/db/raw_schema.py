def ensure_raw_table(cur, table_name: str):

    cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS raw.{table_name} (
                        id SERIAL PRIMARY KEY,
                        data JSONB NOT NULL,
                        _extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """)
    cur.execute(f"ALTER TABLE raw.{table_name} ADD COLUMN IF NOT EXISTS video_id TEXT;")

    cur.execute(f"""
                    CREATE INDEX IF NOT EXISTS ix_raw_{table_name}_extracted_at
                    ON raw.{table_name} (_extracted_at);
        """)

    cur.execute(f"""
                    CREATE INDEX IF NOT EXISTS ix_raw_{table_name}_video_id
                    ON raw.{table_name} (video_id);
        """)

    cur.execute(f"""
                    CREATE INDEX IF NOT EXISTS ix_raw_{table_name}_video_id_extracted_at
                    ON raw.{table_name} (video_id, _extracted_at);
        """)
