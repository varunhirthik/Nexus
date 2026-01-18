#!/bin/sh
# This script ensures nginx uses the PORT environment variable
# Cloud Run sets PORT dynamically

if [ -n "$PORT" ]; then
    sed -i "s/listen 8080/listen $PORT/" /etc/nginx/conf.d/default.conf
fi
