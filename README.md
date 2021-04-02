# nut_supervisor

## Overview
Provides a program that can start and manage nut when it is being used to talk to CyberPower UPS devices.

The driver going out to lunch for these devices is a well known issue and hasn't improved at all recently.

So what this does is provide to the startup and management of the driver. It will periodically check on all the UPSes in the system, and if the client returns a stale data error, it will try to cleanly restart the driver. If it can't, it will force kill them as well and then restart.

Thus far, I've only tested it connected to a single UPS, but it seems to work reliably. I have had it running for days at a time and it does appear, to the outside user, to result in a UPS status that is always there.

## Docker
I've also included a Dockerfile that will make a nice all-in-one container that will install nut and its dependencies, do a basic configuration, and monitor the UPS from there.

It uses [s6](https://skarnet.org/software/s6/) and [s6-overlay](https://github.com/just-containers/s6-overlay) for service management and setup. The image is based on [python:3.8-alpine](https://hub.docker.com/layers/python/library/python/3.8-alpine/images/sha256-2247bddccc66c086a5acfffb7a2316b7cc0a302cc859273c6ede7d4a3e8de202?context=explore) for size reasons. It also turns out nut is readily available in the Alpine packages.

### Example Dockerfile
```docker
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
```

## Docker Compose
I also provided a docker-compose.yml template. You can map in a volume to the containers /etc/nut if you want to manage the files and settings outside of the container (I do).

You also need to map in the USB device. You can either do the whole bus tree or a sepcific device.

### Example Docker Compose
```yaml
---
version: '3'
services:
  supervised_nut:
    image: cyberpowernut:0.1
    container_name: supervised_nut
    volumes:
      - /path/to/private/nut_supervisor/etc-nut:/etc/nut
    ports:
      - 3493:3493
    devices:
      - "/dev/bus/usb:/dev/bus/usb"
    restart: unless-stopped
```
