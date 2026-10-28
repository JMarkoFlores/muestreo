FROM n8nio/n8n:1.75.2
USER root
COPY entrypoint.mjs /usr/local/bin/sentinelbank-n8n-entrypoint.mjs
RUN chown node:node /usr/local/bin/sentinelbank-n8n-entrypoint.mjs
USER node
ENTRYPOINT ["node", "/usr/local/bin/sentinelbank-n8n-entrypoint.mjs"]
