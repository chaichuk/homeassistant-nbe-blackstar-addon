# Будуємо на офіційній базі Home Assistant add-ons
ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

# Пакети
RUN apk add --no-cache bash jq curl python3 py3-pip

# Python-залежності
RUN pip3 install --no-cache-dir paho-mqtt pyduro

# Робоча тека
WORKDIR /app

# Скрипт запуску
COPY run.sh /run.sh
RUN chmod +x /run.sh

# За замовчуванням запускаємо run.sh
CMD ["/run.sh"]

