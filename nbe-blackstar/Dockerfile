ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

RUN apk add --no-cache bash jq curl python3 py3-pip

# venv для залежностей (обхід PEP 668)
RUN python3 -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir paho-mqtt pyduro requests

ENV PATH="/opt/venv/bin:${PATH}"
WORKDIR /app

# автономний скрипт
COPY main.py /app/main.py

# запусковий скрипт
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
