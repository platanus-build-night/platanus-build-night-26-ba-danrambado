#!/bin/bash
# Bootstrap Let's Encrypt SSL for serendiplab.com
# Run this ONCE on the VPS before starting the full stack.
# Usage: ./init-letsencrypt.sh your@email.com

set -e

EMAIL="${1:-}"
DOMAINS=("serendiplab.com" "www.serendiplab.com")
PRIMARY_DOMAIN="${DOMAINS[0]}"
RSA_KEY_SIZE=4096
DATA_PATH="./certbot"
COMPOSE_FILE="docker-compose.prod.yml"

if [ -z "$EMAIL" ]; then
  echo "Usage: ./init-letsencrypt.sh your@email.com"
  exit 1
fi

# ── 1. Download recommended TLS parameters ────────────────────────────────────
if [ ! -e "$DATA_PATH/conf/options-ssl-nginx.conf" ] || [ ! -e "$DATA_PATH/conf/ssl-dhparams.pem" ]; then
  echo "==> Downloading recommended TLS parameters..."
  mkdir -p "$DATA_PATH/conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf \
    > "$DATA_PATH/conf/options-ssl-nginx.conf"
  curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem \
    > "$DATA_PATH/conf/ssl-dhparams.pem"
fi

# ── 2. Create a temporary self-signed cert so nginx can start ─────────────────
echo "==> Creating temporary self-signed certificate..."
mkdir -p "$DATA_PATH/conf/live/$PRIMARY_DOMAIN"
docker compose -f "$COMPOSE_FILE" run --rm --entrypoint \
  "openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout /etc/letsencrypt/live/$PRIMARY_DOMAIN/privkey.pem \
    -out    /etc/letsencrypt/live/$PRIMARY_DOMAIN/fullchain.pem \
    -subj   '/CN=localhost'" \
  certbot

# ── 3. Start nginx with the dummy cert ───────────────────────────────────────
echo "==> Starting nginx..."
docker compose -f "$COMPOSE_FILE" up --force-recreate -d nginx

# ── 4. Delete dummy cert and request real one from Let's Encrypt ─────────────
echo "==> Removing temporary certificate..."
docker compose -f "$COMPOSE_FILE" run --rm --entrypoint \
  "rm -Rf /etc/letsencrypt/live/$PRIMARY_DOMAIN \
          /etc/letsencrypt/archive/$PRIMARY_DOMAIN \
          /etc/letsencrypt/renewal/$PRIMARY_DOMAIN.conf" \
  certbot

echo "==> Requesting Let's Encrypt certificate..."
DOMAIN_ARGS=""
for domain in "${DOMAINS[@]}"; do
  DOMAIN_ARGS="$DOMAIN_ARGS -d $domain"
done

docker compose -f "$COMPOSE_FILE" run --rm --entrypoint \
  "certbot certonly --webroot -w /var/www/certbot \
    --email $EMAIL \
    $DOMAIN_ARGS \
    --rsa-key-size $RSA_KEY_SIZE \
    --agree-tos \
    --force-renewal" \
  certbot

# ── 5. Reload nginx with the real cert ───────────────────────────────────────
echo "==> Reloading nginx..."
docker compose -f "$COMPOSE_FILE" exec nginx nginx -s reload

echo ""
echo "==> SSL certificate obtained successfully!"
echo "    Now start the full stack:"
echo ""
echo "      docker compose -f docker-compose.prod.yml up -d --build"
echo "      docker compose -f docker-compose.prod.yml exec backend uv run python seed.py"
echo ""
