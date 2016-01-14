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
from gi.repository import Gtk, GLib, Gdk, GdkPixbuf

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

DBusGMainLoop(set_as_default=True)
#TODO look into GDBus instead of dbus

bus = dbus.SessionBus()
container_proxy = bus.get_object('org.freedesktop.container', '/org/freedesktop/container')
container_iface = dbus.Interface(container_proxy, dbus_interface='org.freedesktop.container')


from docker import Client
docker_client = Client(base_url='unix://var/run/docker.sock')

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

def get_container_name(container_id):
    container = get_container(container_id)
    """return a list of all container, or return a list that matches the filter"""
    container_info = docker_client.inspect_container(container)
    return container_info['Name']

def get_container_forwards(container_info):
    ports = []
    ports_forwarded = ''
    
    localhost = '127.0.0.1'
    dockerhost = container_info['NetworkSettings']['IPAddress']
    
    for port in container_info['NetworkSettings']['Ports'].keys():
        ports = ''.join([l for l in port if l.isdigit()])
        if container_info['NetworkSettings']['Ports'].get(port):
            if port == '5900/tcp': #  vnc 
                yield 'vnc://%s:%s' % (localhost, container_info['NetworkSettings']['Ports'][port][0].get('HostPort'))
            if port == '443/tcp': #  https
                yield 'https://%s:%s' % (container_info['NetworkSettings']['IPAddress'], container_info['NetworkSettings']['Ports'][port][0].get('HostPort'))
            #  default to http
            yield 'http://%s:%s' % (container_info['NetworkSettings']['IPAddress'], container_info['NetworkSettings']['Ports'][port][0].get('HostPort'))
    #~ return ports_forwarded

class application_gui:
    """Tutorial 13 custom treeview list boxes"""
    count = 0

    retrieve_job = None

    def __init__(self):
        #load in our glade interface
        xml = Gtk.Builder()
        xml.add_from_file('gdocker.glade')

        #grab our widget using get_object this is the name of the widget from glade, window1 is the default name
        self.window = xml.get_object('winFetcher')

        #load our widgets from the glade file
        self.widgets = {}
        self.widgets['searchentry'] = xml.get_object('entry1')
        self.widgets['searchentry'].connect('changed', self.refresh_list)
        self.widgets['listbox'] = xml.get_object('listbox1')
        self.widgets['progress'] = xml.get_object('listProgress')
        self.widgets['refresh'] = xml.get_object('btnRefresh')
        self.widgets['refresh'].connect('button_press_event', self.refresh_list)
        self.widgets['close'] = xml.get_object('btnClose')
        self.widgets['close'].connect('button_press_event', self.closeFetcher)

        #wrap the listbox so we can reuse the code, pass in the listbox widget to our wrapper class
        self.listbox = ListBoxSelect(self.widgets['listbox'])

        #connect to events, in this instance just quit our application
        self.window.connect('delete_event', Gtk.main_quit)
        self.window.connect('destroy', lambda quit: Gtk.main_quit())

        #show the window else there is nothing to see :)
        self.openFetcher()
        self.refresh()

    def openFetcher(self):
        self.window.show_all()

    def refresh_list(self, widget, *args):
        search = None
        if isinstance(widget, Gtk.Entry):
            search = widget.get_text()
        self.refresh(search)

    def refresh(self, filter_string=None):
        """ get a new xml and start the progress bar"""
        self.listbox.clear()

        for container in get_containers(filter=filter_string):
            container_info = docker_client.inspect_container(container['Id'])
            link = None
            ports = [port for port in get_container_forwards(container_info)]
            if ports:
                print link
                link = ports[0]
            
            #~ menu_container = gtk.MenuItem(container_info['Name'])
            self.listbox.model_append(container, '', container_info['Name'], 'test', link)

    def closeFetcher(self, widget):
        self.window.hide()

class ListBoxSelect:
    """ handle the listbox rows dynamically add and remove widgets, and handle download. """
    listbox = None
    gui_rows = {}  # store widgets here so we can destroy them later.

    def __init__(self, listbox):
        """ pass in list box to manage and connect event"""
        self.listbox = listbox
        self.listbox.connect('row-activated', self.selection)
        container_proxy.connect_to_signal("state_change", self.update, dbus_interface="org.freedesktop.container")

    def selection(self, lbox, lbrow):
        """ row selected we may want to react here"""
        container_id = lbrow.get_name()
        boxrow = lbrow.get_children()[0]
        boxinfo = boxrow.get_children()[1]
        print(boxinfo.get_children()[1].get_text())

        print get_container_name(container_id)
        container_name = get_container_name(container_id)
        subprocess.call(
            ['gnome-terminal', '--tab', '-e', '''/bin/bash -c "echo 'Connecting to conatiner named %s';sudo docker exec -it xe_container /bin/bash"''' % (container_name,container_name)])
        print 'background'

    def model_append(self, container, image, title, description, link):
        """ create new widgets, and connect events for our new row"""
        items = {}
        items['row'] = Gtk.ListBoxRow()
        items['row'].set_name(container.get('Id'))
        items['vbox'] = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        items['label1'] = Gtk.Label('%s [%s]' % (title, container.get('Status')), xalign=0)
        items['vbox'].pack_start(items['label1'], True, False, 0)
        
        if link:
            items['label2'] = Gtk.LinkButton(uri=link, label=link, xalign=0)
            items['vbox'].pack_start(items['label2'], True, False, 0)
        #~ items['progress'] = Gtk.ProgressBar()
        #~ items['progress'].hide()
        #~ items['progress'].set_fraction(0) 

        #~ items['vbox'].pack_start(items['label2'], True, False, 0)
        #~ items['vbox'].pack_start(items['progress'], False, False, 0)

        items['hbox'] = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        items['image'] = Gtk.Image.new_from_icon_name('computer-fail' if self.is_container_running(container) else 'computer', 48)
        items['switch'] = Gtk.Switch()#label="Start/Stop"
        items['switch'].set_active(False if 'Exited' in container.get('Status') else True)
        items['switch'].connect('state-set', self.container_toggle_status, container)

        items['button'] = Gtk.Button(label='Remove')
        items['button'].connect('button_press_event', self.container_delete, items['row'], container)
        #~ items['button'].set_fraction(0) 

        items['hbox'].pack_start(items['image'], False, False, 0)
        items['hbox'].pack_start(items['vbox'], True, True, 0)
        items['button_box'] = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        items['button_box'].pack_end(items['button'], False, False, 0)
        items['button_box'].pack_end(items['switch'], False, False, 0)
        items['hbox'].pack_start(items['button_box'], False, False, 0)
        items['row'].add(items['hbox'])

        self.listbox.add(items['row'])
        items['row'].show_all()

        self.gui_rows[container['Id']] = items

    def is_container_running(self, container):
        if 'Exited' in container.get('Status'):
            return True
        return False

    def update(self, container_id):
        print 'container daemon state change'
        print container_id
        #~ state = container_iface.container_status(container_id)
        #~ print state
        #~ self.gui_rows[container['Id']]['switch'].get_state()
        #~ self.gui_rows[container_id]['switch'].set_state(state)

    def container_state_change(self, container_id):
        
        print 'async callback'
        print container_id
        state = container_iface.container_status(container_id)
        print state

        #~ if state != self.gui_rows[container_id]['switch'].get_active():
            #~ self.gui_rows[container_id]['switch'].set_active(state)
        self.gui_rows[container_id]['row'].set_sensitive(True)

    def container_change_status(self, container, state):
        if state is False:
            print 'stopping'
            container_iface.container_stop(container.get('Id'), reply_handler=self.container_state_change, error_handler=self.container_state_change)
            return 
        print 'starting'
        container_iface.container_start(container.get('Id'), reply_handler=self.container_state_change, error_handler=self.container_state_change)
        return False

    def container_toggle_status(self, widget, test,  container):
        self.gui_rows[container.get('Id')]['row'].set_sensitive(False)
        self.container_change_status(container, widget.get_active())
        return

    def container_delete(self, widget, test,  row, container):
        self.listbox.remove(row)
        print('TODO actually remove the container')
        print row
        print container
        return

    #~ def download(self, widget, args, items, link):
        #~ """ download button click, change widgets and start the progress bar and download """
        #~ items['button'].hide()
        #~ items['job'] = subprocess.Popen(
            #~ ['curl', '-O', link],
            #~ shell=False,
            #~ stdout=subprocess.PIPE,
            #~ stderr=subprocess.PIPE)

        #~ GLib.timeout_add_seconds(1, self.update_active_progress_bar, items)

    def update_active_progress_bar(self, widgets):
        """ update progress bar until command finished """
        widgets['progress'].pulse()
        if widgets['job'].poll():
            return True
        widgets['progress'].hide()
        return False

    def clear(self):
        """ remove all rows so we can pre-populate"""
        for item in self.gui_rows.values():
            item['row'].destroy()
        self.gui_rows = {}

application = application_gui()

#~ GObject.mainloop.run()
Gtk.main()