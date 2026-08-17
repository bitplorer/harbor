#!/bin/sh
set -eu
cd /workspace
if curl -sf -o /dev/null --max-time 2 http://127.0.0.1:8080/health; then
  exit 0
fi
if [ ! -s /workspace/assets/css/output.css ]; then
  npx --yes @tailwindcss/cli -i /workspace/assets/css/input.css -o /workspace/assets/css/output.css --minify >>/tmp/harbor-css.log 2>&1 || true
fi
export DEBUG="${DEBUG:-1}"
export WITH_CHANNEL="${WITH_CHANNEL:-1}"
export WITH_HMR=0
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --log-level info >>/tmp/app-startup.log 2>&1 &
i=0
while [ "$i" -lt 40 ]; do
  if curl -sf -o /dev/null --max-time 1 http://127.0.0.1:8080/health; then
    exit 0
  fi
  i=$((i + 1))
  sleep 0.25
done
exit 1
