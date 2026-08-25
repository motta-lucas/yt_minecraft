ARG AIRFLOW_VERSION=2.9.2
ARG PYTHON_VERSION=3.11

FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

USER root

COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /uvx /bin/

RUN /bin/uv --version

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

ENV AIRFLOW_HOME=/opt/airflow

COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

RUN /bin/uv export \
    --no-dev \
    --format requirements-txt \
    -o requirements.txt

USER root

RUN /bin/uv pip install \
    --no-cache-dir \
    --system \
    -r requirements.txt

RUN /bin/uv pip install --no-cache-dir --system -e .

USER airflow

COPY --chown=airflow:root dbt/ /opt/airflow/dbt/
