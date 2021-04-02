#!/bin/sh
if [ ! -f /etc/nut/nut.conf ]; then
    echo "MODE=none" > /etc/nut/nut.conf
fi

if [ ! -f /etc/nut/ups.conf ]; then

    cat > /etc/nut/ups.conf << EOF
[cp850avr]
    desc = "Cyber Power 850 AVR"
    driver = usbhid-ups
    port = auto
    pollinterval = 10
EOF
fi
if [ ! -f /etc/nut/upsd.conf ]; then
    cat > /etc/nut/upsd.conf << EOF
MAXAGE 25
LISTEN 0.0.0.0 3493
EOF
fi
if [ ! -f /etc/nut/upsd.users ]; then
    cat > /etc/nut/upsd.users << EOF
[admin]
    password = adminpassword
    actions = set
    actions = fsd
    instcmds = all

[monitor]
    password = apipassword
    upsmon master
EOF
fi
if [ ! -f /etc/nut/upsmon.conf ]; then
    cat > /etc/nut/upsmon.conf << EOF
MONITOR cp850avr@localhost 1 monitor apipassword master
SHUTDOWNCMD "echo cmd"
DEADTIME 25
EOF
fi

mkdir -p /var/run/nut
chown -R nut:nut /var/run/nut
chgrp -R nut /dev/bus/usb

chmod ugo+x /usr/sbin/supervisor.py
