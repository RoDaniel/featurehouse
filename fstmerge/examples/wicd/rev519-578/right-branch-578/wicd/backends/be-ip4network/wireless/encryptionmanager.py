import os
from templatemanager import TemplateManager
import misc
from misc import WicdError
import wpath
import logging
class EncryptionError(WicdError): pass
class EncryptionManager(object):
    def __init__(self, interface_name):
        self.interface_name = interface_name
        self.template_manager = TemplateManager()
        self.template_manager.load_all_available_templates()
    def start(self, network):
        self.stop()
        profile = network.profile
        if not 'encryption_type' in network.profile:
            raise EncryptionError(
                'Network profile does not specify encryption type'
            )
        encryption_type = network.profile['encryption_type']
        template_class = self.template_manager.get_template(encryption_type)
        if not template_class:
            raise EncryptionError(
                'Template type %s does not exist' % encryption_type
            )
        values = {}
        for requirement in template_class.require:
            if requirement.name in profile:
                values[requirement.name] = str(profile[requirement.name])
            else:
                raise EncryptionError(
                    'Encryption error: missing required value %s'
                    % requirement.name
                )
        values['essid'] = network.essid
        values['scan'] = 0
        logging.debug('wpa_supplicant values %s', values)
        wpa_conf_name = network.bssid.replace(':', '').lower()
        wpa_conf_name += '-vpb'
        wpa_conf_name += '-' + str(self.interface_name)
        self.create_configuration_file(wpa_conf_name, template_class, values)
        pathname = os.path.join(wpath.networks, wpa_conf_name)
        self.wpa_supplicant = misc.run([
            misc.find_program_in_path('wpa_supplicant'), '-i', 
            self.interface_name, '-D', 'wext', '-c', pathname
        ], include_stderr=True, return_fileobject=True)
    def stop(self):
        if hasattr(self, 'wpa_supplicant'):
            logging.debug('killing wpa_supplicant %s', self.wpa_supplicant.pid)
            os.kill(self.wpa_supplicant.pid, 15)
        else:
            logging.debug('no wpa_supplicant running')
    def __del__(self):
        self.stop()
    def __copy__(self): return self
    def __deepcopy__(self, memo): return self
    def create_configuration_file(self, filename, template_class, values):
        wpa_supplicant_template = str(template_class.template)
        for key, value in values.iteritems():
            value = str(value)
            find = "$_%s" % key.upper()
            logging.debug('replacing %s with %s', find, value)
            wpa_supplicant_template = \
                                    wpa_supplicant_template.replace(find, value)
        pathname = os.path.join(wpath.networks, filename)
        logging.debug('writing wpa_supplicant configuration file %s', pathname)
        the_file = open(pathname, 'w')
        the_file.write(wpa_supplicant_template)
        the_file.close()
