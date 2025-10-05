ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:latest
FROM ${BUILD_FROM}

RUN apk add --no-cache bash jq curl python3 py3-pip

# venv для pip (PEP 668)
RUN python3 -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir paho-mqtt pyduro

ENV PATH="/opt/venv/bin:${PATH}"
WORKDIR /app

# наш автономний main.py усередину образу
COPY main.py /app/main.py

# запусковий скрипт
COPY run.sh /run.sh
RUN chmod +x /run.sh

CMD ["/run.sh"]
