#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
( cd "$ROOT/frontends/portfolio" && npm install && npm run build )
( cd "$ROOT/frontends/nexus-learning-web" && npm install && npm run build )
echo "frontends built: portfolio/dist, nexus-learning-web/dist"
