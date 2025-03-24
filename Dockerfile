FROM python:3.9-slim   # 기존: python:3.9
# slim 버전: 기본 파이썬 기능만 포함한 가벼운 버전

RUN apt-get update && apt-get install -y \
    wget \            # 크롬 설치에 필요
    gnupg \          # 크롬 설치에 필요
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \  # 크롬 브라우저 설치