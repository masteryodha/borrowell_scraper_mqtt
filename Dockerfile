FROM python:3.11-slim

ENV MQTT_URL=localhost \
    MQTT_PORT=1883 \
    MQTT_USER=mqtt_user \
    MQTT_PASSWORD=mqtt_password \
    WEB_USER=web_user \
    WEB_PASSWORD=web_password \
    DEBIAN_FRONTEND=noninteractive \
    MYTIMEZONE=America/Montreal \
    PLATFORM=docker \
    PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

# Installer dépendances système nécessaires pour Playwright
RUN apt-get update && apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libasound2 libpangocairo-1.0-0 \
    libpango-1.0-0 libcairo2 libatspi2.0-0 wget curl \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python, Playwright et les navigateurs
# On installe juste chromium pour réduire la taille de l'image
COPY requirements.txt ./
RUN pip install --no-cache-dir playwright -r requirements.txt \
    && playwright install chromium --with-deps

COPY . .

EXPOSE 8080

#-u is necessary to get logs of the python script in docker logs
#CMD ["python3", "-u", "./getCreditBorrowell.py"]
CMD ["python3", "-u", "./getScheduled.py"]
