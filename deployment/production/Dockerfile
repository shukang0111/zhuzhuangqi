FROM python:3
ENV PYTHONUNBUFFERED 1

USER root

RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak

COPY deployment/production/shigongbao/sources.list /etc/apt/

RUN apt-get update

RUN apt-get install -y libreoffice

RUN mkdir -p /data/zhuzhuangqi/zhuzhuangqi-backend/

RUN mkdir -p /var/log/operation_logs/

WORKDIR /data/zhuzhuangqi/zhuzhuangqi-backend/

COPY ./ /data/zhuzhuangqi/zhuzhuangqi-backend/

# COPY deployment/production/shigongbao/production.sh /etc/profile.d/

# RUN chmod 777 /etc/profile.d/production.sh

RUN chmod 777 deployment/production/scripts/start.sh

RUN chmod 777 deployment/production/shigongbao/start_server.sh

COPY deployment/production/shigongbao/requirements.txt /etc/

COPY deployment/production/shigongbao/gunicorn.conf /etc/

RUN pip install -i http://pypi.douban.com/simple/ -r /etc/requirement.txt --trusted-host pypi.douban.com



