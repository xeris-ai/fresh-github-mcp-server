#!/bin/bash

# extract script directory
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
cd "${SCRIPT_DIR}" || exit 1
# Check if uv is installed
if ! command -v uv &>/dev/null; then
  echo "uv is not installed. Please install it using 'pip install uv'."
  exit 1
fi

if [ ! -d "${SCRIPT_DIR}/.venv" ]; then
  echo "Creating virtual environment..."
  if ! uv venv "${SCRIPT_DIR}/.venv" >/dev/null 2>&1; then
    echo >&2 "Failed to create virtual environment. Please check your Python installation."
    exit 1
  fi
fi

if ! uv pip install -e . -qq >/dev/null >&1; then
  echo >&2 "Failed to install the package. Please check your setup."
  exit 1
fi

if ! source ${SCRIPT_DIR}/.venv/bin/activate >/dev/null >&1; then
  echo >&2 "Failed to activate virtual environment. Please check if .venv exists."
  exit 1
fi

python -m app.server
