import os
import logging
class BaseDhcpClient(object):
    def __init__(self, interface_name, profile):
        self.interface_name = interface_name
        self.profile = profile
    def start(self):
        raise NotImplementedError('start is not implemented in this class')
    def stop(self):
        raise NotImplementedError('stop is not implemented in this class')
    def status(self):
        return True
    def check(self):
        return True
    def __del__(self):
        raise NotImplementedError('__del__ is not implemented in this class')
    def _setup_configuration_file(self):
        options = ['subnet-mask', 'broadcast-address', 'time-offset', 'routers',
	'domain-name', 'domain-name-servers', 'host-name']
        for item in options:
            value = self.profile.get('dhcp_get_' + item)
            if not value is None:
                if not value:
                    logging.debug('dhclient will not request %s', item)
                    options.remove(item)
        return options
