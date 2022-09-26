FROM python:3.9-slim-bullseye
LABEL maintainer="edenceHealth <info@edence.health>"

# os-level deps
RUN set -x \
  && export DEBIAN_FRONTEND=noninteractive \
  && apt-get -yq update \
  && apt-get -yq install --no-install-recommends \
    build-essential \
    freetds-dev \
    python-dev \
    strace \
    unixodbc-dev \
  && rm -rf /var/lib/apt/lists/*

# app-level deps (do these separately first to leverage the build cache)
ARG RUNTIME_PROFILER
ENV RUNTIME_PROFILER=${RUNTIME_PROFILER}
COPY ["requirements.txt", "/"]
RUN set -x \
  && pip install -r /requirements.txt \
  && if [ -n "${RUNTIME_PROFILER}" ]; then pip install py-spy; fi \
  && pip cache purge \
  && rm -rf /usr/local/lib/python*/site-packages/awscli/examples

ARG LOG_DIR
ARG VOCABULARY_DIR
ENV LOG_DIR=${LOG_DIR:-/logs} \
  INPUT_DIR=${VOCABULARY_DIR:-/input}

# create a non-root account for the code to run with
ARG USER_UID=1000
RUN set -eux \
  && useradd \
    --no-log-init \
    --base-dir / \
    --home-dir "/home/user" \
    --create-home \
    --no-user-group \
    --shell "/bin/bash" \
    --uid "${USER_UID}" \
    "user" \
  && passwd \
    --lock \
    "user" \
  && mkdir -p "$INPUT_DIR" "$LOG_DIR" \
  && chown user "$INPUT_DIR" "$LOG_DIR"

# copy app code
ARG GIT_COMMIT
ARG GIT_TAG
ENV GIT_COMMIT=${GIT_COMMIT:-Unspecified} \
  GIT_TAG=${GIT_TAG:-Unspecified}
COPY ["entrypoint.sh", "/"]
COPY ["app/", "/app/"]

WORKDIR /app

USER user
ENTRYPOINT ["/entrypoint.sh"]
