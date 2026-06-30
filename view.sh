#!/usr/bin/env bash
#
# view.sh — serve the .excalidraw file locally and open it in the browser.
#
# Usage:  ./view.sh [port]
#
set -euo pipefail

PORT="${1:-8765}"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
URL="http://localhost:${PORT}/view.html"

cd "$REPO_DIR"

# Check the .excalidraw file exists
if [[ ! -f "transformers-talk.excalidraw" ]]; then
  echo "Error: transformers-talk.excalidraw not found."
  echo "Run: python3 gen_excalidraw_file.py"
  exit 1
fi

# Check view.html exists
if [[ ! -f "view.html" ]]; then
  echo "Error: view.html not found."
  exit 1
fi

echo "Serving transformers-talk.excalidraw on http://localhost:${PORT}"
echo "Opening browser to ${URL}"
echo "Press Ctrl-C to stop."
echo ""

# Start the HTTP server in the background
python3 -m http.server "$PORT" &
SERVER_PID=$!

# Give the server a moment to start
sleep 1

# Open the browser (macOS)
if command -v open &>/dev/null; then
  open "$URL"
elif command -v xdg-open &>/dev/null; then
  xdg-open "$URL"
elif command -v wslview &>/dev/null; then
  wslview "$URL"
else
  echo "Could not auto-open browser. Open this URL manually: ${URL}"
fi

# Wait for the server process to be killed (Ctrl-C)
trap "kill $SERVER_PID 2>/dev/null; exit 0" INT TERM
wait $SERVER_PID
