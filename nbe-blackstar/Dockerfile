# Базовий образ для add-ons (amd64 підхопить Supervisor; для інших архівів теж ок)
ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

# Пакети
RUN apk add --no-cache bash jq curl python3 py3-pip

# Створюємо venv і ставимо залежності туди (обхід PEP 668)
RUN python3 -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir paho-mqtt pyduro

# Додаємо venv у PATH, щоб 'python3' і 'pip' вказували на /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

# Робоча тека
WORKDIR /app

# Скрипт запуску
COPY run.sh /run.sh
RUN chmod +x /run.sh

# Запуск
CMD ["/run.sh"]
