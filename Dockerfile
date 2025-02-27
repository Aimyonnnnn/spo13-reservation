FROM python:3.9-slim

# 타임존 설정
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 필요한 시스템 라이브러리 설치
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 비루트 사용자 생성
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 크롬 드라이버 디렉토리 생성 및 권한 설정
RUN mkdir -p /app/.wdm/drivers && \
    chown -R appuser:appuser /app

# 애플리케이션 복사
COPY . .
RUN chown -R appuser:appuser /app

# 사용자 전환
USER appuser

# 환경변수 설정
ENV WDM_LOCAL_PATH=/app/.wdm/drivers

# 실행
CMD ["python", "spo13.py"]
