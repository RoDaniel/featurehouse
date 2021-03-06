from baseplugin import BasePlugin
import logging
class ScanPlugin(BasePlugin):
    ''' A plugin that will trigger wireless scan automatically. '''
    PRIORITY = 0
    def __init__(self, *args):
        BasePlugin.__init__(self, *args)
        self.next_trigger_autoconnect = False
    def do_start(self):
        ''' Triggers a wireless interface scan. '''
        logging.debug('scan plugin started...')
        for interface in self.daemon.interface_manager.get_all_by_type('wireless'):
            interface.do_scan()
