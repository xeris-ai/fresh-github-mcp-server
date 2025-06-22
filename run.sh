#!/bin/bash
#
# This script sets up the Python environment and runs the server.
#
# It ensures 'uv' is installed, creates a virtual environment, and installs
# dependencies from the current project.
#
# USAGE:
#   ./run.sh                    - Silently installs dependencies and runs the server.
#   ./run.sh --install          - Verbosely installs dependencies, does not run the server.
#   ./run.sh -- --app-arg       - Passes arguments to the python server.

# Exit immediately if a command exits with a non-zero status.
# Treat unset variables as an error.
# The return value of a pipeline is the status of the last command to exit
# with a non-zero status, or zero if no command exited with a non-zero status.
set -euo pipefail

# --- Configuration ---
# Get the absolute directory of the script
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
VENV_DIR="${SCRIPT_DIR}/.venv"

# This variable will be set to 1 if --install is passed.
# It controls the verbosity of the script.
INSTALL_ONLY=0

# --- Main Logic ---
main() {
  # Change to the script's directory to ensure relative paths work correctly
  cd "${SCRIPT_DIR}"

  # Simple argument parsing. If the first argument is --install, set the flag.
  if [[ "${1:-}" == "--install" ]]; then
    INSTALL_ONLY=1
    echo "Install-only mode: The server will not be started."
    # In install mode, we shift the argument so it's not passed to the app
    shift
  fi

  # --- Environment Setup ---
  check_uv
  setup_venv
  install_dependencies

  # --- Application Execution ---
  if [ "${INSTALL_ONLY}" -eq 1 ]; then
    echo "✅ Environment setup complete. Exiting as requested."
    exit 0
  fi

  run_server "$@"
}

# --- Helper Functions ---

# Checks if the 'uv' command is available in the system's PATH.
# This function only outputs to stderr on failure, which is desired.
check_uv() {
  if ! command -v uv &>/dev/null; then
    echo >&2 "Error: 'uv' is not installed or not in your PATH."
    echo >&2 "Please install it, for example using: 'pip install uv'"
    exit 1
  fi
}

# Creates the virtual environment using 'uv' if it doesn't already exist.
setup_venv() {
  if [ ! -d "${VENV_DIR}" ]; then
    if [ "${INSTALL_ONLY}" -eq 1 ]; then
      echo "🔎 Virtual environment not found. Creating one in '${VENV_DIR}'..."
    fi
    # 'uv venv' is quiet, but we redirect stdout just in case to ensure silence.
    uv venv >/dev/null
    if [ "${INSTALL_ONLY}" -eq 1 ]; then
      echo "✅ Virtual environment created."
    fi
  fi
}

# Installs the project dependencies in editable mode using 'uv'.
install_dependencies() {
  if [ "${INSTALL_ONLY}" -eq 1 ]; then
    echo "📦 Installing/updating dependencies..."
    # In install mode, we want to see the full output from uv.
    uv pip install -e .
    echo "✅ Dependencies installed."
  else
    # In normal (silent) mode, use the --quiet flag to suppress all
    # non-error output. Errors will still be printed to stderr.
    uv pip install --quiet -e .
  fi
}

# Runs the Python server, passing all script arguments to it.
# 'exec' replaces the shell process with the python process.
run_server() {
  # No "Starting server..." message for a clean stdout.
  exec "${VENV_DIR}/bin/python" -m app.server "$@"
}

# --- Script Entrypoint ---
main "$@"
