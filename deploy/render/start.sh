#!/usr/bin/env sh
set -eu

cd /var/www/html

if [ -n "${RENDER_EXTERNAL_URL:-}" ] && [ -z "${APP_URL:-}" ]; then
  export APP_URL="${RENDER_EXTERNAL_URL}"
fi

if [ -n "${APP_KEY:-}" ] && ! printf '%s' "${APP_KEY}" | grep -q '^base64:'; then
  export APP_KEY="base64:${APP_KEY}"
fi

mkdir -p \
  bootstrap/cache \
  storage/app/public \
  storage/framework/cache/data \
  storage/framework/sessions \
  storage/framework/views \
  storage/logs

chown -R www-data:www-data storage bootstrap/cache || true

if [ ! -e public/storage ]; then
  php artisan storage:link --force --no-interaction || true
fi

if [ "${AUTO_WAIT_FOR_DB:-true}" = "true" ] && [ "${DB_CONNECTION:-}" = "pgsql" ]; then
  DB_HOST_VALUE="${DB_HOST:-}"
  DB_PORT_VALUE="${DB_PORT:-5432}"
  DB_USER_VALUE="${DB_USERNAME:-}"
  DB_NAME_VALUE="${DB_DATABASE:-}"

  if [ -z "${DB_HOST_VALUE}" ] && [ -n "${DB_URL:-}" ]; then
    DB_HOST_VALUE="$(php -r '$url = parse_url(getenv("DB_URL")); echo $url["host"] ?? "";')"
    DB_PORT_VALUE="$(php -r '$url = parse_url(getenv("DB_URL")); echo $url["port"] ?? "5432";')"
    DB_USER_VALUE="$(php -r '$url = parse_url(getenv("DB_URL")); echo isset($url["user"]) ? rawurldecode($url["user"]) : "";')"
    DB_NAME_VALUE="$(php -r '$url = parse_url(getenv("DB_URL")); echo isset($url["path"]) ? ltrim($url["path"], "/") : "";')"
  fi

  if [ -n "${DB_HOST_VALUE}" ]; then
    echo "[render-start] waiting for postgres at ${DB_HOST_VALUE}:${DB_PORT_VALUE}"
    until pg_isready -h "${DB_HOST_VALUE}" -p "${DB_PORT_VALUE}" -U "${DB_USER_VALUE}" -d "${DB_NAME_VALUE}" >/dev/null 2>&1; do
      sleep 2
    done
  fi
fi

if [ "${AUTO_MIGRATE:-true}" = "true" ]; then
  echo "[render-start] php artisan migrate --force"
  php artisan migrate --force --no-interaction
fi

if [ "${AUTO_SEED:-true}" = "true" ]; then
  echo "[render-start] php artisan db:seed --force"
  php artisan db:seed --force --no-interaction
fi

if [ "${AUTO_OPTIMIZE:-true}" = "true" ]; then
  echo "[render-start] php artisan optimize"
  php artisan optimize --no-interaction
fi

exec apache2-foreground
