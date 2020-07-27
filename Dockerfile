FROM python:latest
EXPOSE 8081
WORKDIR /1kbwc-app
COPY ./requirements.txt /1kbwc-app/
RUN cd /1kbwc-app && pip3 install -r requirements.txt
COPY . /1kbwc-app/

CMD ["/usr/local/bin/python3", "-m", "bwc.server"]
