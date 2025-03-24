# 빌드 단계
FROM python:3.9-alpine AS builder

# 빌드에 필요한 패키지 설치
RUN apk add --no-cache \
    wget \
    gnupg \
    build-base \
    libpng-dev \
    freetype-dev \
    libstdc++ \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /etc/apk/keys/chrome.gpg \
    && echo "https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apk/sources \
    && apk update \
    && apk add --no-cache \
        chromium \
        libglib2.0 \
        libpango-1.0

# 작업 디렉토리 설정
WORKDIR /app

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir torch==2.0.0 torchvision==0.15.0 -f https://download.pytorch.org/whl/torch_stable.html \
    && pip install --no-cache-dir -r requirements.txt

# 최종 이미지 단계
FROM python:3.9-alpine

# 런타임에 필요한 패키지만 설치
RUN apk add --no-cache \
    chromium \
    libglib2.0 \
    libpango-1.0 \
    && rm -rf /var/cache/apk/*

# 작업 디렉토리 설정
WORKDIR /app

# 빌드 단계에서 설치된 Python 패키지 복사
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# 애플리케이션 코드 복사
COPY . .

# 실행 명령어
CMD ["python", "main.py"]