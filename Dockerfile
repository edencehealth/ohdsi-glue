FROM edence/pyodbcbase:latest
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
    python3-dev \
    strace \
    unixodbc-dev \
  ; \
  pip install --no-cache-dir --break-system-packages -r /requirements.txt; \
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

# create input and log dir and give nonroot user access
RUN set -eux; \
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
ENTRYPOINT ["/usr/bin/python", "-m", "glue"]
