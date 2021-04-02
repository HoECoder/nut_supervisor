FROM python:3.8-alpine
ARG NUT_VERSION=2.7.4-r8

ADD https://github.com/just-containers/s6-overlay/releases/download/v2.2.0.1/s6-overlay-amd64-installer /tmp/
RUN chmod +x /tmp/s6-overlay-amd64-installer && /tmp/s6-overlay-amd64-installer /

RUN echo '@testing http://dl-cdn.alpinelinux.org/alpine/edge/testing' \
      >>/etc/apk/repositories && \
    apk add --update nut@testing=$NUT_VERSION \
      libcrypto1.1 libssl1.1 musl net-snmp-libs && \
      pip install proc click && \
      mkdir /usr/sbin/nut_supervisor

COPY init_scripts/* /etc/cont-init.d
COPY nut_supervisor/ /usr/sbin/nut_supervisor
COPY supervisor.py /usr/sbin

EXPOSE 3493

ENTRYPOINT ["/init"]
CMD [ "/usr/sbin/supervisor.py", "start", "-c", "500" ]