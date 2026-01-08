#!/bin/sh
set -e

# Domyślnie czyta dane z volume: /data/plakaty.json
API_URL=${API_URL:-/data/posters.json}

# Generujemy config.js przy starcie kontenera
cat > /usr/share/nginx/html/config.js <<EOF
window.__API_URL__ = "${API_URL}";
EOF

exec "$@"
