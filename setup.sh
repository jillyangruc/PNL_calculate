#!/usr/bin/env bash
# setup.sh — Prepare environment for calculate_pnl.py on Linux/WSL/macOS
# - Creates a Python virtual environment .venv
# - Installs required packages from requirements.txt
# - Provides next-step instructions

set -euo pipefail

echo "[1/5] Checking Python..."
if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 not found. Install Python 3.9+ and re-run." >&2
  exit 1
fi

PYVER=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Using Python ${PYVER}"

echo "[2/5] Ensuring pip is available..."
if ! python3 -m pip --version >/dev/null 2>&1; then
  echo "pip not found, attempting to install..."
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update && sudo apt-get install -y python3-pip
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y python3-pip
  elif command -v yum >/dev/null 2>&1; then
    sudo yum install -y python3-pip
  else
    echo "Please install pip for Python 3 manually, then re-run." >&2
    exit 1
  fi
fi

echo "[3/5] Creating virtual environment (.venv)..."
# Try using venv, install if missing on Debian/Ubuntu
if ! python3 -m venv --help >/dev/null 2>&1; then
  echo "python3-venv not found, attempting to install..."
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update && sudo apt-get install -y python3-venv
  else
    echo "Please install the Python venv module manually and re-run." >&2
    exit 1
  fi
fi
python3 -m venv .venv

echo "[4/5] Activating venv and installing dependencies..."
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
else
  # fallback
  pip install pandas
fi

echo "[5/5] Done."
echo
echo "Next steps:"
echo "  source .venv/bin/activate"
echo "  python calculate_pnl.py trades.csv fifo    # or lifo"
echo
echo "Tip: Deactivate with 'deactivate'."
