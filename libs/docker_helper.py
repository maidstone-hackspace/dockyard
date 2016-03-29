#!/usr/bin/env python
# [SNIPPET_NAME: gtk3 listbox example]
# [SNIPPET_CATEGORIES: opengl]
# [SNIPPET_TAGS: touch, gtk3]
# [SNIPPET_DESCRIPTION: add rows to a listbox based on retrieved xml file]
# [SNIPPET_AUTHOR: Oliver Marks ]
# [SNIPPET_LICENSE: GPL]
import os
import requests
import time
from io import StringIO, BytesIO
import subprocess
from lxml.html import parse
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, GLib, Gdk, GdkPixbuf
from gi.repository import Notify as notify
import settings
##import gdocker_logs

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

notify.init(settings.APPINDICATOR_ID)

DBusGMainLoop(set_as_default=True)
#TODO look into GDBus instead of dbus

bus = dbus.SessionBus()
try:
    container_proxy = bus.get_object('org.freedesktop.container', '/org/freedesktop/container')
    container_iface = dbus.Interface(container_proxy, dbus_interface='org.freedesktop.container')
except:
    print("Failed to connect to dbus service, please correct this first.")
    container_proxy = None
    container_iface = None

app_name = "Docker"

from docker import Client
docker_client = Client(base_url='unix://var/run/docker.sock')
print dir(docker_client)

def get_containers(filter=None):
    """return a list of all container, or return a list that matches the filter"""
    for container in docker_client.containers(all=True):
        container_info = docker_client.inspect_container(container['Id'])
        if filter is None or filter in container_info['Name']:
            yield container


def get_container(container_id):
    for container in get_containers():
        if container_id == container['Id']:
            return container


def get_container_info(container_id):
    return docker_client.inspect_container(container_id)


def get_container_logs(container_id, time):
    #since=time is not in docker-py 1.3 which is packaged 
    return docker_client.logs(container=get_container(container_id), timestamps=True)


def get_container_forwards(container_info):
    ports = []
    ports_forwarded = ''
    
    local = True
    localhost = '127.0.0.1'
    dockerhost = container_info['NetworkSettings']['IPAddress']

    if not container_info['NetworkSettings']['Ports']:
        return

    for port in container_info['NetworkSettings']['Ports'].keys():
        ports = ''.join([l for l in port if l.isdigit()])
        if not container_info['NetworkSettings']['Ports'].get(port):
            continue
            
        host = localhost
        hostport = container_info['NetworkSettings']['Ports'][port][0].get('HostPort')
        if local is False:
            host = container_info['NetworkSettings']['IPAddress']
            hostport = ''.join([i for i in port if i.isdigit()])

        if port == '5900/tcp': #  vnc 
            yield 'vnc://%s:%s' % (host, hostport)
        if port == '443/tcp': #  https
            yield 'https://%s:%s' % ((host, hostport))
        #  default to http
        yield 'http://%s:%s' % ((host, hostport))


def get_registry_images(url, version='v2', search=None):
    print search
    dangling_image = 0
    if version == 'l':
        try:
            results = docker_client.images()
        except requests.exceptions.ConnectionError:
            results = []
            print("Docker api not available")
        for item in results:
            labels = item.get('Labels')
            if item.get('RepoTags') == ['<none>:<none>']:
                dangling_image += 1
                continue
            if search in item.get('RepoTags')[0]:
                yield {'name': item.get('RepoTags')[0]}
    else:
        final_url = '%s/%s/' % (url, version)
        if search:
            final_url += 'search?q=%s' % search
        else:
            final_url += '_catalog'
        r = requests.get(final_url)
        registry = r.json()

        for item in registry.get('results' if version=='v1' else 'repositories'):
            print item
            yield item


