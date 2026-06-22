#!/usr/bin/env bash
set -e

# 首次为 www.shiyuan-wreg.cloud 申请 Let's Encrypt 证书
# 运行前请确保: 域名 A 记录已指向本机,本机 80 端口对外开放

DOMAIN="www.shiyuan-wreg.cloud"
EMAIL="${1:-}"

if [ -z "$EMAIL" ]; then
    echo "用法: bash deploy/init-ssl.sh your-email@example.com"
    exit 1
fi

echo "正在为 $DOMAIN 申请 SSL 证书(邮箱: $EMAIL)..."

docker run -it --rm \
    -p 80:80 \
    -v "/etc/letsencrypt:/etc/letsencrypt" \
    -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
    certbot/certbot certonly --standalone \
    -d "$DOMAIN" \
    --agree-tos \
    --non-interactive \
    -m "$EMAIL"

echo "证书申请完成。请检查 /etc/letsencrypt/live/$DOMAIN/"
