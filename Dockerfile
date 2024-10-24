# Copyright 2023 Google, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START cloudrun_helloworld_dockerfile]
# [START run_helloworld_dockerfile]

# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.12

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True
ENV PORT=8080
ARG APP_USER=appuser
ARG APP_GROUP=appgroup
ARG COMPANY_NAME="HCA Healthcare"
ARG ORGANIZATION_NAME="Public Cloud Engineering"
ARG DEPARTMENT_NAME="Container Platform Administration"
LABEL company="${COMPANY_NAME}"
LABEL organization="${ORGANIZATION_NAME}"
LABEL department="${DEPARTMENT_NAME}"
# DO NOT remove or modify the following label as it is used by the included
# GitHub Actions workflow.
LABEL version=$IMAGE_VERSION
# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt \
    && set -ex \
    # Create a non-root user
    && addgroup --system --gid 9000 appgroup \
    && adduser --system --uid 1001 --gid 9000 --no-create-home appuser \
    && chown -R 1001:9000 $APP_HOME 
# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app

# [END run_helloworld_dockerfile]
# [END cloudrun_helloworld_dockerfile]
