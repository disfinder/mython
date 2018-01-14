FROM alpine:latest
LABEL maintainer="3998461+disfinder@users.noreply.github.com"
LABEL version = '1.0'
WORKDIR /opt/app
COPY ./lib/ ./lib/
COPY ./scripts/ ./scripts/
COPY requirements.txt ./


RUN apk add --update \
  bash \
  python-dev \
  py-pip \
  py-setuptools \
  ca-certificates \
  gcc \
  musl-dev \
  linux-headers \
  libffi-dev\
  openssl-dev && \
  pip install --upgrade pip && \
  pip install --upgrade --no-cache-dir pip setuptools python-openstackclient \
  && apk del gcc musl-dev linux-headers \
  && rm -rf /var/cache/apk/* \
  && pip install --upgrade -r requirements.txt

ENV PYTHONPATH "/opt/app"
CMD [ "python", "./scripts/pf9/audit.py", "-h" ]
