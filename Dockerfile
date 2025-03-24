# 빌드 단계
FROM python:3.9-slim AS builder

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libxss1 \
    libappindicator1 \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 실행 단계
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    libxss1 \
    libappindicator1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/bin/google-chrome /usr/bin/google-chrome
COPY --from=builder /usr/lib/chromium /usr/lib/chromium
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . /app
WORKDIR /app

CMD ["python", "spo13.py"]
