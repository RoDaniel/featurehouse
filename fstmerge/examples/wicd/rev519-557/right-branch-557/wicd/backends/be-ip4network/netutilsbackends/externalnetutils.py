import re
import os
import misc
import basenetutils
class InterfaceRegexPatterns:
    ip          = re.compile(r'inet [Aa]d?dr[^.]*:([^.]*\.[^.]*\.[^.]*\.[0-9]*)', re.S)
class NetworkInterface(basenetutils.BaseNetworkInterface):
    ''' Represents a network interface. '''
    def up(self):
        ''' Put the interface up. '''
        cmd = [misc.find_program_in_path('ifconfig'), self.interface_name, 'up']
        misc.run(cmd)
    def down(self):
        ''' Put the interface down. '''
        cmd = [misc.find_program_in_path('ifconfig'), 
               self.interface_name, 'down']
        misc.run(cmd)
    def get_ip(self):
        """ Get the IP address of the interface.
        Returns:
        The IP address of the interface in dotted quad form.
        """
        cmd = '%s %s' % (misc.find_program_in_path('ifconfig'),
                         self.interface_name)
        output = misc.run(cmd)
        return misc.run_regex(InterfaceRegexPatterns.ip, output)
    def set_ip(self, new_ip):
        ''' Sets the IP of the current network interface. '''
        cmd = '%s %s %s' % (misc.find_program_in_path('ifconfig'), 
                            self.interface_name, new_ip)
        misc.run(cmd)
    def set_netmask(self, new_ip):
        ''' Sets the netmask of the current network interface. '''
        cmd = '%s %s netmask %s' % (misc.find_program_in_path('ifconfig'), 
                            self.interface_name, new_ip)
        misc.run(cmd)
    def set_gateway(self, new_ip):
        ''' Sets the netmask of the current network interface. '''
        cmd = '%s add default gateway %s %s' % (misc.find_program_in_path('route'), 
                            new_ip, self.interface_name)
        misc.run(cmd)
    def check_link(self):
        """ Get the current physical connection state.
        The method will first attempt to use ethtool do determine
        physical connection state.  Should ethtool fail to run properly,
        mii-tool will be used instead.
        Returns:
        True if a link is detected, False otherwise.
        """
        sys_device = '/sys/class/net/%s/' % self.interface_name
        carrier_path = os.path.join(sys_device, 'carrier')
        if not self.is_up():
            self.up()
        if os.path.exists(carrier_path):
            try:
                carrier = open(carrier_path, 'r')
                link = int(carrier.read().strip())
                if link == 1:
                    return True
                elif link == 0:
                    return False
            except (IOError, ValueError, TypeError):
                log('%s: error checking link using /sys/class/net/%s/carrier'
                      % (self.interface_name, self.interface_name))
                return False
    def is_up(self):
        """ Determines if the interface is up.
        Returns:
        True if the interface is up, False otherwise.
        """
        flags_file = '/sys/class/net/%s/flags' % self.interface_name
        try:
            flags = open(flags_file, "r").read().strip()
        except IOError:
            print "Could not open %s, using ifconfig to determine status" % flags_file
            return self._slow_is_up()
        return bool(int(flags, 16) & 1)
    def _slow_is_up(self, ifconfig=None):
        """ Determine if an interface is up using ifconfig. """
        cmd = [misc.find_program_in_path("ifconfig"), self.interface_name]
        output = misc.run(cmd)
        lines = output.split('\n')
        if len(lines) < 5:
            return False
        for line in lines[1:4]:
            if line.strip().startswith('UP'):
                return True   
        return False
