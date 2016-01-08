#!/usr/bin/env/python3
# This file is /home/me/test-dbus.py
# Remember to make it executable if you want dbus to launch it
# It works with both Python2 and Python3

from gi.repository import Gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

from docker import Client
docker_client = Client(base_url='unix://var/run/docker.sock')


def get_containers(filter=None):
    """return a list of all container, or return a list that matches the filter"""
    for container in docker_client.containers(all=True):
        container_info = docker_client.inspect_container(container['Id'])
        if filter is None or filter in container_info['Name']:
            yield container


class ContainerService(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName('org.freedesktop.container', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/org/freedesktop/container')

    def is_container_running(self, container):
        container_status = docker_client.inspect_container(container).get('State', {})
        print container_status.get('Status', '')
        if 'Exited' in container_status.get('Status', ''):
            return False
        return True

    def tmp_list(self):
        print [c.get('Id') for c in get_containers()]

    @dbus.service.method(dbus_interface='org.freedesktop.container', in_signature='s', out_signature='s')
    def container_stop(self, container_id):
        print docker_client.stop(container_id)
        self.tmp_list()
        return str(self.is_container_running(container_id))

    @dbus.service.method(dbus_interface='org.freedesktop.container', in_signature='s', out_signature='s')
    def container_start(self, container_id):
        self.tmp_list()
        return str(self.is_container_running(container_id))

    #~ @dbus.service.method(dbus_interface='org.freedesktop.container', in_signature='s', out_signature='s')
    #~ def container_run_tty(self, container_id, run):
        #~ return str(self.is_container_running(container_id))

    @dbus.service.method(dbus_interface='org.freedesktop.container', in_signature='s', out_signature='s')
    def container_logs(self, container_id):
        return str(self.is_container_running(container_id))



#~ c8ba2c6c41a86147eaad3a1959f84e19cdf3b7c520e2cb596782165331be3978


print [c.get('Id') for c in get_containers()]
DBusGMainLoop(set_as_default=True)
myservice = ContainerService()
Gtk.main() 
