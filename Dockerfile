FROM ubuntu:20.04
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get \
  upgrade -o Dpkg::Options::=--force-confold \
  -o Dpkg::Options::=--force-confdef \
  -y --allow-downgrades --allow-remove-essential --allow-change-held-packages && \
  DEBIAN_FRONTEND=noninteractive apt-get \
  install -o Dpkg::Options::=--force-confold \
  -o Dpkg::Options::=--force-confdef \
  -y --allow-downgrades --allow-remove-essential --allow-change-held-packages python3-pip nginx
COPY ./requirements.txt /1kbwc-app/
RUN cd /1kbwc-app && pip3 install -r requirements.txt
COPY package-support/run.sh /1kbwc-app/
COPY package-support/1kbwc.service /etc/systemd/system
EXPOSE 80
COPY package-support/nginx.conf /etc/nginx/nginx.conf
COPY ./*.py /1kbwc-app/
COPY static /srv/http
COPY ./cards /1kbwc-app/cards

CMD ['/bin/sh' '/1kbwc-app/run.sh']
