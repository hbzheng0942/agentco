#!/usr/bin/env bash
# feishu_push.sh "message" — 出站推送(自定义机器人webhook,支持加签)
set -euo pipefail
source "$(dirname "$0")/../.env" 2>/dev/null || true
[ -z "${FEISHU_WEBHOOK:-}" ] && { echo "FEISHU_WEBHOOK unset"; exit 0; }
MSG=$(printf '%s' "$1" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
if [ -n "${FEISHU_SECRET:-}" ]; then
  TS=$(date +%s)
  # 飞书加签:以 "timestamp\nsecret" 为HMAC密钥,对空串签名
  SIGN=$(printf '' | openssl dgst -sha256 -mac HMAC -macopt "key:$(printf '%s\n%s' "$TS" "$FEISHU_SECRET")" -binary | base64)
  EXTRA="\"timestamp\":\"$TS\",\"sign\":\"$SIGN\","
else EXTRA=""; fi
curl -s -m 10 -X POST "$FEISHU_WEBHOOK" -H 'Content-Type: application/json' \
  -d "{${EXTRA}\"msg_type\":\"text\",\"content\":{\"text\":$MSG}}" > /dev/null
