FROM python:3.11-slim
LABEL maintainer="edenceHealth <info@edence.health>"

COPY requirements.txt /

ARG DEBIAN_FRONTEND=noninteractive
ARG AG="apt-get -yq --no-install-recommends"
RUN set -eux; \
  $AG update; \
  $AG upgrade; \
  $AG install \
    build-essential \
    freetds-dev \
    python-dev \
    strace \
    unixodbc-dev \
  ; \
  pip install -r /requirements.txt; \
  pip cache purge; \
  $AG purge \
    build-essential \
    python-dev \
  ; \
  $AG clean; \
  $AG autoremove; \
  rm -rf \
    /var/lib/apt/lists/* \
    /usr/local/lib/python*/site-packages/awscli/examples \
  ;

ARG LOG_DIR
ARG VOCABULARY_DIR
ENV LOG_DIR=${LOG_DIR:-/logs} \
  INPUT_DIR=${VOCABULARY_DIR:-/input}

# create a non-root account for the code to run with
ARG NONROOT_UID=65532
ARG NONROOT_GID=65532
RUN set -eux; \
  groupadd --gid "${NONROOT_GID}" "nonroot"; \
  useradd \
    --no-log-init \
    --base-dir / \
    --home-dir "/home/user" \
    --create-home \
    --shell "/bin/bash" \
    --uid "${NONROOT_UID}" \
    --gid "${NONROOT_GID}" \
    "nonroot" \
  ; \
  passwd --lock "nonroot"; \
  mkdir -p "$INPUT_DIR" "$LOG_DIR"; \
  chown nonroot:nonroot "$INPUT_DIR" "$LOG_DIR";

# copy app code
ARG GIT_COMMIT
ARG GIT_TAG
ENV GIT_COMMIT="${GIT_COMMIT:-0000000000000000000000000000000000000000}" \
  GIT_TAG="${GIT_TAG:-DEV-BUILD}"
COPY ["src/glue/", "/app/glue/"]

ENV PYTHONPATH="/app"
WORKDIR /work

USER nonroot
ENTRYPOINT ["/usr/local/bin/python3", "-m", "glue"]
