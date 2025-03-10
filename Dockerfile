FROM python:3.9-slim

# 타임존 설정
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 필요한 시스템 라이브러리 설치 (Chrome과 ChromeDriver 실행에 필요)
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libpango-1.0-0 \
    libgbm1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Chrome 134.0.6998.35 설치 (zip 파일 방식)
RUN wget -O /tmp/chrome-linux64.zip "https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.35/linux64/chrome-linux64.zip" && \
    unzip /tmp/chrome-linux64.zip -d /opt/ && \
    rm /tmp/chrome-linux64.zip && \
    ln -s /opt/chrome-linux64/chrome /usr/local/bin/google-chrome && \
    chmod 755 /usr/local/bin/google-chrome

# ChromeDriver 134.0.6998.35 설치
RUN wget -O /tmp/chromedriver-linux64.zip "https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.35/linux64/chromedriver-linux64.zip" && \
    unzip /tmp/chromedriver-linux64.zip -d /usr/local/bin/ && \
    mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    rm -rf /usr/local/bin/chromedriver-linux64 && \
    rm /tmp/chromedriver-linux64.zip && \
    chmod 755 /usr/local/bin/chromedriver

WORKDIR /app

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 복사
COPY . .

# 캐시 경로 권한 설정 및 초기화
RUN mkdir -p /tmp/chrome-data && chmod -R 777 /tmp/chrome-data && \
    mkdir -p /.cache/selenium && chmod -R 777 /.cache/selenium && \
    rm -rf /root/.config/google-chrome

# 실행
CMD ["python", "spo13.py"]
