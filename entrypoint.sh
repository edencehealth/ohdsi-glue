#!/bin/sh 
set -e

export LOG_DIR="${LOG_DIR:-/logs}"
export INPUT_DIR="${VOCABULARY_DIR:-/input}"
PROFILE_DIR="${PROFILE_DIR:-/profiles}"

warn() {
  printf '%s %s\n' "$(date '+%FT%T')" "ENTRYPOINT $*" >&2
}

die() {
  warn "FATAL:" "$@"
  exit 1
}

main() {
  warn "ohdsi_glue container started -- running as $(id)"

  # define the command to run the app
  set -- python main.py "$@"

  if [ -n "$RUNTIME_PROFILER" ]; then
    # the RUNTIME_PROFILER environment variable is defined as a build arg to
    # the container build process, it is then exported as an ENV. if set at
    # build time it triggers installation of the profiler package
    if [ -d "$PROFILE_DIR" ]; then
      warn "Profile directory (${PROFILE_DIR}) detected. Running with profiler."
      # prepend the py-spy command
      set -- py-spy record \
        -o "${PROFILE_DIR}/$(date '+%Y%m%d%H%M%S').svg" \
        -- \
        "$@"
    else
      warn "This is a profiler-included container image but the profile" \
        "directory (${PROFILE_DIR}) was not found; running without profiler"
    fi
  fi

  # run the actual command
  set -x
  "$@"
}

main "$@"; exit