import wpath, misc
from logfile import log
import netutils, configmanager
from logfile import log
class NetworkProfile(object):
    def __init__(self, settings={}):
        self.__values = {}
        if settings:
            for key, value in settings.iteritems():
                self[key] = value
    def __setitem__(self, key, value):
        self.__values[key] = misc.smart_type(value)
    def __getitem__(self, key):
        return self.__values[key]
    def __contains__(self, item):
        return item in self.__values
    def __delitem__(self, item):
        del self.__values[item]
    def __iter__(self):
        return self.__values.iteritems()
    def __len__(self):
        return len(self.__values)
class ProfiledNetworkInterface(netutils.NetworkInterface):
    ''' Adds network profiles to the wireless interface. '''
    def __init__(self, interface_name):
        netutils.NetworkInterface.__init__(self, interface_name)
        self.config_manager = configmanager.ConfigManager(wpath.etc + 
                                                          '%s-profiles.conf'
                                                          % interface_name)
    def _save_config(self, config_list, identifier):
        for item in config_list:
            for key, value in item:
                self.config_manager.set_option(item[identifier], key, value)
        self.config_manager.write()
