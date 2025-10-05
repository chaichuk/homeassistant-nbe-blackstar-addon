ARG BUILD_FROM=ghcr.io/hassio-addons/base:16.2.3
FROM ghcr.io/e1z0/nbe-blackstar-homeassistant:latest as upstream

FROM ${BUILD_FROM}
RUN apk add --no-cache bash jq
COPY --from=upstream /app /app
COPY run.sh /run.sh
RUN chmod +x /run.sh
CMD ["/run.sh"]
