import os
from datetime import datetime, timedelta

import pendulum
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount

local_tz = pendulum.timezone("America/Sao_Paulo")

DBT_IMAGE = "ghcr.io/dbt-labs/dbt-postgres:1.7.0"
DBT_HOST_DIR = os.environ["DBT_HOST_DIR"]
DBT_PROJECT_DIR = "/usr/app/yt_minecraft_dbt"
DBT_PROFILES_DIR = "/usr/app/profiles"

default_args = {
    "owner": "motta-lucas",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2026, 9, 1, tzinfo=local_tz),
}

common_env = {
    "DBT_PROJECT_DIR": DBT_PROJECT_DIR,
    "DBT_PROFILES_DIR": DBT_PROFILES_DIR,
    "DBT_TARGET": os.environ.get("DBT_TARGET", "dev"),
    "POSTGRES_CONN_HOST": os.environ.get("POSTGRES_CONN_HOST", "postgres"),
    "POSTGRES_CONN_PORT": os.environ.get("POSTGRES_CONN_PORT", "5432"),
    "ELT_DATABASE_NAME": os.environ["ELT_DATABASE_NAME"],
    "ELT_DATABASE_USERNAME": os.environ["ELT_DATABASE_USERNAME"],
    "ELT_DATABASE_PASSWORD": os.environ["ELT_DATABASE_PASSWORD"],
}

common_mounts = [Mount(source=DBT_HOST_DIR, target="/usr/app", type="bind")]

with DAG(
    dag_id="dbt_youtube_pipeline",
    default_args=default_args,
    description="dbt staging and core for youtube data",
    schedule=None,
    catchup=False,
    tags=["dbt", "youtube"],
) as dag:

    dbt_run_staging = DockerOperator(
        task_id="dbt_run_staging",
        image=DBT_IMAGE,
        docker_url="unix:///var/run/docker.sock",
        network_mode="airflow-net",
        command=(
            f"run "
            f"--project-dir {DBT_PROJECT_DIR} "
            f"--profiles-dir {DBT_PROFILES_DIR} "
            f"--select tag:staging"
        ),
        environment=common_env,
        mounts=common_mounts,
        auto_remove=True,
        mount_tmp_dir=False,
    )

    dbt_test_staging = DockerOperator(
        task_id="dbt_test_staging",
        image=DBT_IMAGE,
        docker_url="unix:///var/run/docker.sock",
        network_mode="airflow-net",
        command=(
            f"test "
            f"--project-dir {DBT_PROJECT_DIR} "
            f"--profiles-dir {DBT_PROFILES_DIR} "
            f"--select tag:staging"
        ),
        environment=common_env,
        mounts=common_mounts,
        auto_remove=True,
        mount_tmp_dir=False,
    )

    dbt_run_core = DockerOperator(
        task_id="dbt_run_core",
        image=DBT_IMAGE,
        docker_url="unix:///var/run/docker.sock",
        network_mode="airflow-net",
        command=(
            f"run "
            f"--project-dir {DBT_PROJECT_DIR} "
            f"--profiles-dir {DBT_PROFILES_DIR} "
            f"--select tag:core"
        ),
        environment=common_env,
        mounts=common_mounts,
        auto_remove=True,
        mount_tmp_dir=False,
    )

    dbt_test_core = DockerOperator(
        task_id="dbt_test_core",
        image=DBT_IMAGE,
        docker_url="unix:///var/run/docker.sock",
        network_mode="airflow-net",
        command=(
            f"test "
            f"--project-dir {DBT_PROJECT_DIR} "
            f"--profiles-dir {DBT_PROFILES_DIR} "
            f"--select tag:core"
        ),
        environment=common_env,
        mounts=common_mounts,
        auto_remove=True,
        mount_tmp_dir=False,
    )

    dbt_run_staging >> dbt_test_staging >> dbt_run_core >> dbt_test_core
