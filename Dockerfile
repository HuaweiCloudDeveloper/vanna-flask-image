FROM python:3.10.14-slim

# 替换APT源
RUN sed -i 's/http:\/\/deb.debian.org\//https:\/\/mirrors.huaweicloud.com\//g' /etc/apt/sources.list.d/debian.sources

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip config set global.index-url https://repo.huaweicloud.com/repository/pypi/simple

WORKDIR /app
COPY requirements.txt .
COPY ./app .

RUN pip install -r requirements.txt
