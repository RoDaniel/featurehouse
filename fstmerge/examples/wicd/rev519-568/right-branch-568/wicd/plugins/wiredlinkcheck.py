from baseplugin import BasePlugin
from misc import WicdError
import gobject
import logging
from wglobals import global_config
class WiredLinkCheckPlugin(BasePlugin):
    ''' A plugin meant to guess your location so that
    Wicd can configure network connections better. '''
    PRIORITY = 1000
    def __init__(self, *args):
        BasePlugin.__init__(self, *args)
        self.last_status = {}
    def do_start(self):
        check_timeout = global_config.get('wiredlinkcheck',
                                          'timeout_seconds', 2)
        gobject.timeout_add_seconds(check_timeout, self.check_status)
        self.check_status()
    def check_status(self):
        interfaces = self.daemon.interface_manager.get_all_by_type('wired')
        for interface in interfaces:
            link = interface.get_has_link()
            if link:
                if self.last_status.get(interface, False) is False:
                    logging.debug( '%s: interface got link', interface.interface_name)
                    self.daemon.plugin_manager.action('got_link', (interface, ))
            self.last_status[interface] = link
        return True
    def do_new_location(self, location):
        interfaces = self.daemon.interface_manager.get_all_by_type('wired')
        for interface in interfaces:
            if self.last_status.get(interface, False):
                self.daemon.plugin_manager.action('got_link', (interface,))
