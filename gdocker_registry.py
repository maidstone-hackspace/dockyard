#!/usr/bin/env/python3
# This file is /home/me/test-dbus.py
# Remember to make it executable if you want dbus to launch it
# It works with both Python2 and Python3

import yaml
import json
from gi.repository import Gtk
from gi.repository import Notify as notify

import settings
from libs.docker_helper import get_registry_images, container_iface


class registry_browser():
    showing_local_images = True
    current_image = ''

    def __init__(self):
        # load in our glade interface
        xml = Gtk.Builder()
        xml.add_from_file('glade/gdocker_registry.glade')

        self.window_run = xml.get_object('window_run')

        self.run_param_container_name = xml.get_object('run_widget_name')
        self.run_param_treeview = xml.get_object('run_widget_list')
        self.run_param_liststore = xml.get_object('run_widget_liststore')
        self.run_widget_launch = xml.get_object('run_widget_launch')
        self.run_widget_add_row = xml.get_object('run_widget_add_row')
        self.run_widget_add_row_param_type = xml.get_object('run_widget_param_type')
        self.run_widget_add_param1 = xml.get_object('run_widget_param1')
        self.run_widget_add_param2 = xml.get_object('run_widget_param2')

        self.run_widget_daemon = xml.get_object('run_widget_daemon')
        self.run_widget_interactive = xml.get_object('run_widget_interactive')
        self.run_widget_terminal = xml.get_object('run_widget_terminal')
        self.run_widget_priviledged = xml.get_object('run_widget_priviledged')
        self.run_widget_add_row.connect('button_press_event', self.add_row_to_container)
        self.run_widget_launch.connect('button_press_event', self.run_widget_launcher)

        self.window = xml.get_object('window_registry')
        self.window.connect('delete_event', self.hide)
        self.widget_image_list = xml.get_object('lb_image_list')
        self.registry_list = xml.get_object('cmb_registrys')
        self.registry_list.connect('changed', self.search_registry)

        self.pull_progress = xml.get_object('image_progress')
        self.search_registry_widget = xml.get_object('image_search')
        self.search_registry_widget.connect('activate', self.search_registry)

        for registry in settings.registry_list:
            self.registry_list.append_text(registry[0])
        self.registry_list.set_active(0)

        for image in get_registry_images('localhost', version='l', search=''):
            self.add_image(image.get('name'))

        self.menu = Gtk.Menu()
        menu_item1 = Gtk.MenuItem("Pull Image")
        menu_item1.connect('activate', self.pull_image)

        menu_remove_image = Gtk.MenuItem("Remove Image")
        menu_remove_image.connect('activate', self.remove_image)

        self.menu.append(menu_item1)
        # self.menu.connect('button_press_event', self.container_delete, items['row'], container)
        menu_item2 = Gtk.MenuItem("Start Container")
        self.menu.append(menu_item2)
        
        self.update_create_properties_from_config()

    def add_row_to_container(self, *args):
        self.run_param_liststore.append([
            self.run_widget_add_row_param_type.get_active_text(),
            self.run_widget_add_param1.get_text(),
            self.run_widget_add_param2.get_text()
        ])
        self.docker_create_container()

    def show(self):
        self.window.show_all()

    def hide(self, *args):
        self.window.hide()
        return True

    def update_create_properties_from_config(self):
        with open('config/default.yaml') as fp:
            properties = yaml.load(fp)

        first_key = properties.keys()[0]
        if type(properties[first_key]) is dict:
            properties = properties[first_key]
        
        print '------------'
        print properties

        self.current_image = properties.get('image', '')
        self.run_param_container_name.set_text(properties.get('container_name', ''))
        self.run_widget_terminal.set_active(properties.get('tty') is True)
        self.run_widget_priviledged.set_active(properties.get('privileged') is True)

        if properties.get('volumes'):
            for v in properties.get('volumes'):
                vol = v.split(':')
                self.run_param_liststore.append([
                    'Volumes',
                    vol[0],
                    vol[-1] if len(vol) > 1 else ''
                ])

        if properties.get('expose'):
            for p in properties.get('expose'):
                port = p.split(':')
                self.run_param_liststore.append([
                    'Ports',
                    port[0],
                    port[-1] if len(port) > 1 else ''
                ])

        if properties.get('links'):
            for p in properties.get('links'):
                port = p.split(':')
                self.run_param_liststore.append([
                    'Links',
                    port[0],
                    port[-1] if len(port) > 1 else ''
                ])

        print properties

    def docker_create_container(self):
        param_list = []
        param_list.append('--name %s' % self.run_param_container_name.get_text())
        print '--name %s' % self.run_param_container_name.get_text()
        
        switches = ''
        switches += 'd' if self.run_widget_daemon.get_active() else ''
        switches += 'i' if self.run_widget_interactive.get_active() else ''
        switches += 't' if self.run_widget_terminal.get_active() else ''
        switches += 'p' if self.run_widget_priviledged.get_active() else ''

        param_list.append('- %s' % switches)
        for switch, value1, value2 in self.run_param_liststore:
            if value2:
                param_list.append('--%s %s:%s' % (switch.lower(), value1, value2))
            else:
                param_list.append('--%s %s' % (switch.lower(), value1))
        print param_list
        
        self.window_run.show_all()

    def container_create_json(self):
        ports = [':'.join((value1, value2)) for switch, value1, value2 in self.run_param_liststore if switch == 'Ports']
        volumes = [':'.join((value1, value2)) for switch, value1, value2 in self.run_param_liststore if switch == 'Volumes']
        enviroment = [':'.join((value1, value2)) for switch, value1, value2 in self.run_param_liststore if switch == 'Enviroment']
        links = [':'.join((value1, value2)) for switch, value1, value2 in self.run_param_liststore if switch == 'Links']

        return {
            'name': self.run_param_container_name.get_text(),
            'image': self.current_image,
            'command': '',
            'hostname': '',
            'detach': True if self.run_widget_daemon.get_active() else False,
            'tty': True if self.run_widget_terminal.get_active() else False,
            'ports': ports,
            'environment': enviroment,
            'volumes': volumes,
            'volumes_from': []
        }

    def run_widget_launcher(self, *args):
        self.window_run.hide()
        self.pull_progress.start()
        container_params = self.container_create_json()
        print 'launch container'
        print container_iface.container_create(json.dumps(container_params), reply_handler=self.docker_message_handler, error_handler=self.docker_message_handler)


    def docker_message_handler(self, container_id):
        self.pull_progress.stop()
        #~ self.populate()

    def pull_image(self, widget, skip, name):
        # pass the image requested to the dbus daemon for download and respond to the callback
        self.pull_progress.start()
        container_iface.image_pull(name, reply_handler=self.docker_message_handler, error_handler=self.docker_message_handler)

    def launch_image(self, widget, skip, name):
        self.window_run.show_all()

    def remove_image(self, widget, skip, name):
        # pass the image requested to the dbus daemon for download and respond to the callback
        container_iface.image_remove(name, reply_handler=self.docker_message_handler, error_handler=self.docker_message_handler)

    def search_registry(self, widget):
        for row in self.widget_image_list.get_children():
            row.destroy()

        registry_url = self.registry_list.get_active_text()
        search_value = self.search_registry_widget.get_text()
        result = [(reg[0], reg[1]) for reg in settings.registry_list if reg[0] == registry_url]

        self.showing_local_images = False
        if registry_url == 'localhost':
            self.showing_local_images = True

        if result:
            registry_url, registry_version = result[0]
            for item in get_registry_images(registry_url, version=registry_version, search=search_value):
                self.add_image(item.get('name'))
            self.widget_image_list.show_all()

    def popup_menu(self, widget, event):
        print 'menu'
        if event.button == 3:
            print 'Right Click'
            self.menu.show_all()
            self.menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

    def add_image(self, name):
        row = Gtk.ListBoxRow()
        row.set_activatable(True)
        row.set_selectable(True)
        row.connect('activate', self.popup_menu)
        label = Gtk.Label(name)
        label.set_justify(Gtk.Justification.LEFT)
        label.set_halign(Gtk.Justification.LEFT)
        label.set_xalign(0)
        layout_box = Gtk.Box()
        layout_box.pack_start(label, True, False, 5)

        if self.showing_local_images is True:
            remove_button = Gtk.Button(label='Remove')
            remove_button.connect('button_press_event', self.remove_image, name)
            layout_box.add(remove_button)
        else:
            pull_button = Gtk.Button(label='Pull')
            pull_button.connect('button_press_event', self.pull_image, name)
            layout_box.add(pull_button)

        run_button = Gtk.Button(label='Run')
        run_button.connect('button_press_event', self.launch_image, name)

        layout_box.add(run_button)

        row.add(layout_box)
        self.widget_image_list.add(row)
