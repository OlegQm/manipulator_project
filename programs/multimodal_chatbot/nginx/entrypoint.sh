#!/bin/sh
# Generate the .htpasswd file from environment variables at container startup.
# This avoids baking credentials into the image.

set -e

if [ -z "$BASIC_AUTH_USER" ] || [ -z "$BASIC_AUTH_PASSWORD" ]; then
    echo "ERROR: BASIC_AUTH_USER and BASIC_AUTH_PASSWORD must be set"
    exit 1
fi

htpasswd -bc /etc/nginx/.htpasswd "$BASIC_AUTH_USER" "$BASIC_AUTH_PASSWORD"
echo "Basic auth configured for user: $BASIC_AUTH_USER"

exec nginx -g 'daemon off;'
