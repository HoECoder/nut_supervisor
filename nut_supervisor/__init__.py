"""Supervisor for NUT processes when using CyberPower UPS

As we all know, CyberPower UPSes sometimes go out to lunch, and the only
way to reliably get it back is to stop upsd and the driver.
"""
#pylint disable=consider-iterating-dictionary

import time
import subprocess
from configparser import ConfigParser
from typing import Mapping, Set
from proc.core import find_processes

UPS_CONF_FILENAME = "/etc/nut/ups.conf"
DRV_CTRL_PROCESS = "/usr/sbin/upsdrvctl"
UPSD_PROCESS = "/usr/sbin/upsd"
DRIVER_PROCESSES = [
    "usbhid-ups"
]
MONITOR_COMMAND = "/usr/bin/upsc"

class NutSupervisor:
    """Provides startup and supervision of the NUT drivers

    Helps handle the problematic CyberPower UPS drivers.
    """
    def __init__(self, monitor_cycle:int=250):
        """Setup the supervisor
        """
        self.monitor_cycle = monitor_cycle
        self.user = "root"
        self.ups_names = None
        self.ups_confs = None
        self.load_ups_conf()
    def load_ups_conf(self):
        """Read NUTs /etc/nut/ups.conf to get the configuration of UPSes here"""
        conf = ConfigParser()
        conf.read(UPS_CONF_FILENAME)
        self.ups_names = [s for s in conf.sections()] #pylint: disable=unnecessary-comprehension
        ups_confs = dict()
        for ups in self.ups_names:
            section = conf[ups]
            ups_confs[ups] = {key: val for key, val in section.items()} #pylint: disable=unnecessary-comprehension
        self.ups_confs = ups_confs
    def startup(self):
        """Starts up the drivers"""
        started = False
        self.start_driver_ctrl()
        return started
    def monitor(self):
        """Starts the drivers and then begins monitoring them"""
        if self.startup():
            time.sleep(0.250)
            self.run()
    def run(self):
        """The main monitoring loop where the state of the drivers is periodically checked"""
        run = True
        while run:
            statuses = self.check_status()
            unhealthy = [ups for ups in statuses.keys() if not statuses[ups]]
            drivers_to_bounce = set()
            for ups in unhealthy:
                driver = self.ups_confs[ups].get('driver', 'usbhid-ups')
                drivers_to_bounce.add(driver)
            if drivers_to_bounce:
                self.bounce_drivers(drivers_to_bounce)
            time.sleep(self.monitor_cycle/1000)
    def bounce_drivers(self, drivers_to_bounce: set):
        """Bounce the given drivers

        First, it shuts down the local upsd (reasons), then attempts to bounce the driver
        control, then bring it all back.
        """
        print(f"Bounced driver on: {int(time.time())}")
        self.stop_upsd()
        self.restart_driver_ctrl(drivers_to_bounce)
        self.start_upsd()
    def start_driver_ctrl(self):
        """Starts upsdrvctl as self.user"""
        try:
            args = [
                DRV_CTRL_PROCESS,
                "-u",
                self.user,
                "start"
            ]
            result = subprocess.run(args, check=True) #pylint: disable=unused-variable
            return True
        except subprocess.CalledProcessError:
            return False
    def restart_driver_ctrl(self, drivers_to_bounce):
        """Attempts to nicely restart the drivers, or hard kills them"""
        if not self.start_driver_ctrl():
            self.hard_stop_drivers(drivers_to_bounce)
            self.start_driver_ctrl()
    def hard_stop_drivers(self, drivers_to_stop: Set[str]):
        """Force-kills the named drivers (literally kill -9)"""
        for process in find_processes():
            if process.comm in drivers_to_stop:
                process.kill()
    def stop_upsd(self):
        """Tries to stop upsd"""
        try:
            args = [
                UPSD_PROCESS,
                "-u",
                self.user,
                "-c",
                "stop"
            ]
            result = subprocess.run(args, check=True) #pylint: disable=unused-variable
            return True
        except subprocess.CalledProcessError:
            return False
    def start_upsd(self) -> bool:
        """Start up upsd"""
        try:
            args = [
                UPSD_PROCESS,
                "-u",
                self.user
            ]
            result = subprocess.run(args, check=True) #pylint: disable=unused-variable
            return True
        except subprocess.CalledProcessError:
            return False
    def check_ups(self, ups): #pylint: disable=no-self-use
        """Check the given UPS"""
        try:
            args = [
                MONITOR_COMMAND,
                f"{ups}@localhost"
            ]
            #pylint: disable=unused-variable
            results = subprocess.run(args, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    def check_status(self) -> Mapping[str, bool]:
        """Check each UPS in turn"""
        ups_stat = {}
        for name in self.ups_names:
            ups_stat[name] = self.check_ups(name)
        return ups_stat
