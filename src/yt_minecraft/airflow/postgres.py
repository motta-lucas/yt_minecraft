from __future__ import annotations

from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import RealDictCursor


def get_conn_cursor(postgres_id: str, database_name: str):
    hook = PostgresHook(postgres_conn_id=postgres_id, database=database_name)
    conn = hook.get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    return conn, cur


def close_conn_cursor(conn, cur):
    cur.close()
    conn.close()
