FROM python:3.9-slim

# 필요한 패키지 설치 (libindicator7 제거, Chrome에 필수적인 의존성만 유지)
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

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY . /app
WORKDIR /app

# 실행 명령어
CMD ["python", "spo13.py"]
