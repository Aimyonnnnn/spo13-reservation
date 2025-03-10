FROM python:3.9-slim

# 타임존 설정
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 필요한 시스템 라이브러리 및 Chrome 특정 버전 설치
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable=134.0.6998.36-1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ChromeDriver 고정 버전 설치 (134.0.6998.35)
RUN wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/134.0.6998.35/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod 755 /usr/local/bin/chromedriver

WORKDIR /app

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 복사
COPY . .

# 캐시 경로 권한 설정
RUN mkdir -p /tmp/chrome-data && chmod -R 777 /tmp/chrome-data && \
    mkdir -p /.cache/selenium && chmod -R 777 /.cache/selenium

# 실행
CMD ["python", "spo13.py"]
