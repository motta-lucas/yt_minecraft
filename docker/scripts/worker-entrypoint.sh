#!/bin/bash
set -e

#Adjust socket Docker permission
if [ -S /var/run/docker.sock ]; then
    chmod 666 /var/run/docker.sock
fi

# Start work as usual
exec su -s /bin/bash airflow -c "airflow celery worker"