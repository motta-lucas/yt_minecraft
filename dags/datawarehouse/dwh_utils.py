from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import RealDictCursor

table = "yt_minecraft_videos"


def get_conn_cursor():
    hook = PostgresHook(postgres_conn_id="postgres_db_yt_elt", database="elt_db_minecraft")
    conn = hook.get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    return conn, cur


def close_conn_cursor(conn, cur):
    cur.close()
    conn.close()


def create_schema(schema):
    conn, cur = get_conn_cursor()

    schema_sql = f"CREATE SCHEMA IF NOT EXISTS {schema};"

    cur.execute(schema_sql)

    conn.commit()

    close_conn_cursor(conn, cur)


def create_table(schema):

    conn, cur = get_conn_cursor()

    if schema == "staging":
        table_sql = f"""
                    CREATE TABLE IF NOT EXISTS {schema}.{table} (
                        "Video_ID" VARCHAR(22) PRIMARY KEY NOT NULL,
                        "Video_Title" TEXT NOT NULL,
                        "Published" TIMESTAMP NOT NULL,
                        "Duration" INT,
                        "View_Count" INT,
                        "Like_Count" INT,
                        "Comment_Count" INT,
                        "Channel_Title" VARCHAR(22) NOT NULL
                        "Channel_ID" VARCHAR(22) NOT NULL
                    );
                    """

    else:
        table_sql = f"""
                    CREATE TABLE IF NOT EXISTS {schema}.{table} (
                        "Video_ID" VARCHAR(22) PRIMARY KEY NOT NULL,
                        "Video_Title" TEXT NOT NULL,
                        "Published" TIMESTAMP NOT NULL,
                        "Duration" INT,
                        "View_Count" INT,
                        "Like_Count" INT,
                        "Comment_Count" INT,
                        "Channel_Title" VARCHAR(22) NOT NULL
                        "Channel_ID" VARCHAR(22) NOT NULL
                    );
                    """

    cur.execute(table_sql)

    conn.commit()

    close_conn_cursor(conn, cur)

def get_videos_data(videosData: dict):

    billboard_list = []

    for key, value in videosData.items():
        billboard_list.append(
            {
                "Artist": value["Artist"],
                "Title": value["Title"],
                "Peak": value["Peak"],
                "Last_Position": value["Last_Position"],
                "Weeks": value["Weeks"],
                "Position": value["Position"],
                "IsNew": value["IsNew"],
                "Input_Date": value["Input_Date"],
            }
        )
    return billboard_list