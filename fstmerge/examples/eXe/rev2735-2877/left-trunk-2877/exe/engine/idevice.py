"""
The base class for all iDevices
"""
import copy
import logging
from copy                 import deepcopy
from exe.engine.persist   import Persistable
from exe.engine.translate import lateTranslate
from exe.engine.resource  import Resource
log = logging.getLogger(__name__)
class Idevice(Persistable):
    """
    The base class for all iDevices
    iDevices are mini templates which the user uses to create content in the 
    package
    """
    nextId = 1
    NoEmphasis, SomeEmphasis, StrongEmphasis = range(3)
    def __init__(self, title, author, purpose, tip, icon, parentNode=None):
        """Initialize a new iDevice, setting a unique id"""
        log.debug("Creating iDevice")
        self.edit        = True
        self.lastIdevice = True
        self.emphasis    = Idevice.NoEmphasis
        self.version     = 0
        self.id          = unicode(Idevice.nextId)
        Idevice.nextId  += 1
        self.parentNode  = parentNode
        self._title      = title
        self._author     = author
        self._purpose    = purpose
        self._tip        = tip
        self.icon        = icon
        self.userResources = []
        if self.icon:
            self.systemResources = ["icon_"+self.icon+".gif"]
        else:
            self.systemResources = []
    def get_title(self):
        """
        Gives a nicely encoded and translated title that can be put inside
        xul labels (eg. <label value="my &quot;idevice&quot;">)
        """
        if not hasattr(self, '_title'):
            self._title = 'NO TITLE'
        if self._title:
            title = _(self._title)
            title = title.replace('&', '&amp;') 
            title = title.replace('"', '&quot;')
            return title
        else:
            return u''
    def set_title(self, value):
        """
        Sets self._title
        """
        self._title = value
    title    = property(get_title, set_title)
    rawTitle = lateTranslate('title')
    author   = lateTranslate('author')
    purpose  = lateTranslate('purpose')
    tip      = lateTranslate('tip')
    def __cmp__(self, other):
        """
        Compare this iDevice with other
        """
        return cmp(self.id, other.id)
    def __deepcopy__(self, others):
        """
        Override deepcopy because normal one seems to skip things when called from resource.__deepcopy__
        """
        miniMe = self.__class__.__new__(self.__class__)
        others[id(self)] = miniMe
        miniMe.userResources = []
        for resource in self.userResources:
            miniMe.userResources.append(deepcopy(resource, others))
        for key, val in self.__dict__.items():
            if key != 'userResources':
                setattr(miniMe, key, deepcopy(val, others))
        miniMe.id = unicode(Idevice.nextId)
        Idevice.nextId += 1
        return miniMe
    def clone(self):
        """
        Clone an iDevice just like this one
        """
        log.debug("Cloning iDevice")
        newIdevice = copy.deepcopy(self)
        return newIdevice
    def delete(self):
        """
        delete an iDevice from it's parentNode
        """
        while self.userResources:
            self.userResources[0].delete()
        if self.parentNode:
            self.parentNode.idevices.remove(self)
            self.parentNode = None
    def isFirst(self):
        """
        Return true if this is the first iDevice in this node
        """
        index = self.parentNode.idevices.index(self)
        return index == 0
    def isLast(self):
        """
        Return true if this is the last iDevice in this node
        """
        index = self.parentNode.idevices.index(self)
        return index == len(self.parentNode.idevices) - 1
    def movePrev(self):
        """
        Move to the previous position
        """
        parentNode = self.parentNode
        index = parentNode.idevices.index(self)
        if index > 0:
            temp = parentNode.idevices[index - 1]
            parentNode.idevices[index - 1] = self
            parentNode.idevices[index]     = temp
    def moveNext(self):
        """
        Move to the next position
        """
        parentNode = self.parentNode
        index = parentNode.idevices.index(self)
        if index < len(parentNode.idevices) - 1:
            temp = parentNode.idevices[index + 1]
            parentNode.idevices[index + 1] = self
            parentNode.idevices[index]     = temp
    def setParentNode(self, parentNode):
        """
        Change parentNode
        """
        if self.parentNode:
            self.parentNode.idevices.remove(self)
        parentNode.addIdevice(self)
    def _upgradeIdeviceToVersion1(self):
        """
        Upgrades the Idevice class members from version 0 to version 1.
        Should be called in derived classes.
        """
        log.debug("upgrading to version 1")
        self._title   = self.__dict__.get('title', self.title)
        self._author  = self.__dict__.get('author', self.title)
        self._purpose = self.__dict__.get('purpose', self.title)
        self._tip     = self.__dict__.get('tip', self.title)
    def _upgradeIdeviceToVersion2(self):
        """
        Upgrades the Idevice class members from version 1 to version 2.
        Should be called in derived classes.
        """
        log.debug("upgrading to version 2, for 0.12")
        self.userResources = []
        if self.icon:
            self.systemResources = ["icon_"+self.icon+".gif"]
        else:
            self.systemResources = []
