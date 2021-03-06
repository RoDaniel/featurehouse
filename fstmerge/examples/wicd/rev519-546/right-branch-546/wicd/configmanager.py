""" Wicd Configuration Manager
Wrapper around ConfigParser for wicd, though it should be
reusable for other purposes as well.
"""
from ConfigParser import ConfigParser
from misc import stringToNone
class ConfigManager(ConfigParser):
    """ A class that can be used to manage a given configuration file. """
    def __init__(self, path):
        ConfigParser.__init__(self)
        self.config_file = path
        self.read(path)
    def __repr__(self):
        return self.config_file
    def __str__(self):
        return self.config_file
    def get_config(self):
        return self.config_file
    def set_option(self, section, option, value, save=False):
        """ Wrapper around ConfigParser.set
        Adds the option to write the config file change right away.
        """
        if not self.has_section(section):
            self.add_section(section)
        ConfigParser.set(self, section, str(option), str(value))
        if save:
            self.write()
    def set(self, *args, **kargs):
        self.set_option(*args, **kargs)
    def get_option(self, section, option, default=None):
        """ Wrapper around ConfigParser.get. 
        Automatically adds any missing sections, adds the ability
        to write a default value, and if one is provided prints if
        the default or a previously saved value is returned.
        """
        if not self.has_section(section):
            self.add_section(section)
        if self.has_option(section, option):
            ret = ConfigParser.get(self, section, option)
            if default:
                print ''.join(['found ', option, ' in configuration ', ret])
        else:
            print ''.join(['did not find ', option,
                           ' in configuration, setting default ', str(default)])
            self.set(section, option, str(default), save=True)
            ret = default
        return ret
    def get(self, *args, **kargs):
        return self.get_option(*args, **kargs)
    def write(self):
        configfile = open(self.config_file, 'w')
        ConfigParser.write(self, configfile)
        configfile.close()
    def remove_section(self,section):
        if self.has_section(section):
            ConfigParser.remove_section(self, section)
    def clear_all(self):
        for section in self.sections():
            self.remove_section(section)
