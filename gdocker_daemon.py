#!/usr/bin/env/python3
# Remember to make it executable if you want dbus to launch it
# It works with both Python2 and Python3
import datetime
import sys
from gi.repository import GLib
import threading
import dbus
import json 
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

from docker import Client
from docker.errors import APIError
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
        print "\nstop container %s" % container_id
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

    @dbus.service.method(dbus_interface='org.freedesktop.container', in_signature='s', out_signature='s')
    def container_create(self, container_params):
        container_params = json.loads(container_params)
        print "\ncreate container %s" % container_params
        try:
            print docker_client.create_container(**container_params)
        except APIError as e:
            print e
        #~ self.tmp_list()
        #~ self.state_change('start')
        print 'finished'
        return 'finished'

    @dbus.service.method(dbus_interface='org.freedesktop.container', in_signature='s', out_signature='s')
    def image_pull(self, image):
        print "\n pull container %s" % image
        for progress in docker_client.pull(image, stream=True):
            print progress
            
        print 'pull complete'
        #~ self.tmp_list()
        #~ self.state_change('start')
        return image

    @dbus.service.method(dbus_interface='org.freedesktop.container', in_signature='s', out_signature='s')
    def container_remove(self, container_id):
        print "\nremove container %s" % container_id
        print docker_client.remove_container(container=container_id, force=True)
        #~ self.tmp_list()
        #~ self.state_change('start')
        return ''

    @dbus.service.signal(dbus_interface='org.freedesktop.container', signature='ss')
    def state_change(self, container_id, state):
        print 'emit signal %s %s' % (container_id, state)
        #~ print "%d bottles of %s on the wall" % (number, contents)
        return 'something changed %s %s' % (container_id, state)

    #~ @dbus.service.method(dbus_interface='org.freedesktop.container', in_signature='s', out_signature='s')
    #~ def container_run_tty(self, container_id, run):
        #~ return str(self.is_container_running(container_id))

    @dbus.service.method(dbus_interface='org.freedesktop.container', in_signature='s', out_signature='s')
    def container_logs(self, container_id):
        return str(self.is_container_running(container_id))


class DockerEventsThread(threading.Thread):
    # TODO look for a better way asyncio perhaps ?
    def __init__(self, service):
        self.service = service
        threading.Thread.__init__(self)

    def run(self):
        now = datetime.datetime.now()
        since = now
        live_events = docker_client.events(since=since)
        while True:
            container = next(live_events)
            container = json.loads(container)
            if container.get('status') in ('start', 'stop', 'create'):
                self.service.state_change(str(container.get('Id')), str(container.get('status')))


#~ c8ba2c6c41a86147eaad3a1959f84e19cdf3b7c520e2cb596782165331be3978

def signal_term_handler(signal, frame):
    print 'got SIGTERM'
    sys.exit(0)
 
print [c.get('Id') for c in get_containers()]
DBusGMainLoop(set_as_default=True)
myservice = ContainerService()
time_in_ms = 120
#~ GObject.timeout_add(time_in_ms, myservice.live_events)
e = DockerEventsThread(myservice)
e.daemon = True
e.start()

now = datetime.datetime.now()
since = now #- datetime.timedelta(seconds=10)
live_events = docker_client.events(since=since)
#~ GObject.io_add_watch (live_events, GObject.IO_IN, myservice.live_events)

try:
    GLib.MainLoop().run()
except KeyboardInterrupt:
    print 'got SIGTERM'
    #~ e.finish()
    sys.exit(0)
