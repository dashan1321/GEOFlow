#!/usr/bin/env sh
set -eu

cd /var/www/html

if [ -n "${RENDER_EXTERNAL_URL:-}" ] && [ -z "${APP_URL:-}" ]; then
  export APP_URL="${RENDER_EXTERNAL_URL}"
fi

if [ -n "${APP_KEY:-}" ] && ! printf '%s' "${APP_KEY}" | grep -q '^base64:'; then
  export APP_KEY="base64:${APP_KEY}"
fi

exec php artisan "$@"
