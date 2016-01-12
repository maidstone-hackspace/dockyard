#!/usr/bin/env/python3
# Remember to make it executable if you want dbus to launch it
# It works with both Python2 and Python3
import datetime
import sys
import time
from gi.repository import GLib, GObject
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

from docker import Client
docker_client = Client(base_url='unix://var/run/docker.sock')


def get_containers(filter=None):
    """return a list of all container, or return a list that matches the filter"""
    docker_client = Client(base_url='unix://var/run/docker.sock')
    for container in docker_client.containers(all=True):
        container_info = docker_client.inspect_container(container['Id'])
        if filter is None or filter in container_info['Name']:
            yield container

def callback(msg):
    print 'method'

def errback(msg):
    print 'method'

class ContainerService(dbus.service.Object):
    live_events = None
    live_events_date = None
    
    def __init__(self):
        bus_name = dbus.service.BusName('org.freedesktop.container', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/org/freedesktop/container')

    def is_container_running(self, container):
        print 'is container running'
        container_status = docker_client.inspect_container(container).get('State', {})
        print container_status.get('Status', '')
        if 'running' in container_status.get('Status', ''):
            return True
        return False

    def tmp_list(self):
        print [c.get('Id') for c in get_containers()]

    def callback(self, msg):
        print 'class'

    #, reply_handler=handler, error_handler=handler
    @dbus.service.method(dbus_interface='org.freedesktop.container', in_signature='s', out_signature='s')
    def container_stop(self, container_id):
        print "\ntop container %s" % container_id
        docker_client.stop(container_id)
        #~ self.tmp_list()
        #~ self.state_change('stop')
        return container_id

    @dbus.service.method(dbus_interface='org.freedesktop.container', in_signature='s', out_signature='s')
    def container_running(self, container_id):
        print "\ncontainer running ~ %s" % container_id
        return str(self.is_container_running(container_id))

    @dbus.service.method(dbus_interface='org.freedesktop.container', in_signature='s', out_signature='s')
    def container_status(self, container_id):
        return str(self.is_container_running(container_id))

    @dbus.service.method(dbus_interface='org.freedesktop.container', in_signature='s', out_signature='s')
    def container_start(self, container_id):
        print "\nstart container %s" % container_id
        print docker_client.start(container_id)
        #~ self.tmp_list()
        #~ self.state_change('start')
        return container_id

    @dbus.service.signal(dbus_interface='org.freedesktop.container')
    def state_change(self, container_id, state):
        print 'emit signal'
        #~ print "%d bottles of %s on the wall" % (number, contents)
        return 'something changed %s' % test

    #~ @dbus.service.method(dbus_interface='org.freedesktop.container', in_signature='s', out_signature='s')
    #~ def container_run_tty(self, container_id, run):
        #~ return str(self.is_container_running(container_id))

    @dbus.service.method(dbus_interface='org.freedesktop.container', in_signature='s', out_signature='s')
    def container_logs(self, container_id):
        return str(self.is_container_running(container_id))

    def live_events(self):
        if self.live_events is None:
            now = datetime.datetime.now()
            since = now #- datetime.timedelta(seconds=10)
            self.live_event = docker_client.events(since=since, stream=True)
        print self.live_events
        return next(self.live_events)
        #~ print 'get events'
        #~ for event in docker_client.events(since=since):
            #~ if event.get('status') == 'start':
                #~ self.state_change(event.get('id'),'start')



#~ c8ba2c6c41a86147eaad3a1959f84e19cdf3b7c520e2cb596782165331be3978

def signal_term_handler(signal, frame):
    print 'got SIGTERM'
    sys.exit(0)
 
print [c.get('Id') for c in get_containers()]
DBusGMainLoop(set_as_default=True)
myservice = ContainerService()
time_in_ms = 120
#~ GObject.timeout_add(time_in_ms, myservice.live_events)

try:
    GLib.MainLoop().run()
except KeyboardInterrupt:
    print 'got SIGTERM'
    sys.exit(0)
