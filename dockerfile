ARG AIRFLOW_VERSION=2.9.3
ARG PYTHON_VERSION=3.11
ARG PYTHON_VERSION_CONSTRAINTS=3.11

FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

ARG AIRFLOW_VERSION
ARG PYTHON_VERSION_CONSTRAINTS

# Prevent docker from shadowing python/pip in ~/.local/bin and avoids user site-packages
ENV PATH=/usr/local/bin:/usr/bin:/bin
ENV PYTHONNOUSERSITE=1

USER root

#uv binaries
COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /uvx /bin/
RUN /bin/uv --version

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Working directiory
ENV AIRFLOW_HOME=/opt/airflow
WORKDIR /opt/airflow

# Optional - grants permission to AIRFLOW_HOME
RUN chown -R airflow:root /opt/airflow

# Airflow Constraints (always major.minor in python)
ENV AIRFLOW_CONSTRAINTS_URL=https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION_CONSTRAINTS}.txt
RUN echo ${AIRFLOW_CONSTRAINTS_URL}

# Copy necessary files from project to pip install
COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

# Install packages + extras from Airflow runtime under constraints
# (extras: providers, docker operator, etc.)
RUN /bin/uv pip install \
    --no-cache-dir \
    --system \
    --constraint ${AIRFLOW_CONSTRAINTS_URL} \
    -e ".[airflow]"

RUN rm -rf /home/airflow.local/bin/python /home/airflow/.local/bin/pip /home/airflow/.local/lib/python* || true

USER airflow