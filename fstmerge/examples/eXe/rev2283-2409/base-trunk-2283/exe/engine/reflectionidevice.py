"""
A Reflection Idevice presents question/s for the student to think about
before they look at the answer/s
"""
import logging
from exe.engine.idevice   import Idevice
from exe.engine.translate import lateTranslate
log = logging.getLogger(__name__)
class ReflectionIdevice(Idevice):
    """
    A Reflection Idevice presents question/s for the student to think about
    before they look at the answer/s
    """
    persistenceVersion = 6
    def __init__(self, activity = "", answer = ""):
        """
        Initialize 
        """
        Idevice.__init__(self, 
                         x_(u"Reflection"),
                         x_(u"University of Auckland"), 
                         x_(u"""Reflection is a teaching method often used to 
connect theory to practice. Reflection tasks often provide learners with an 
opportunity to observe and reflect on their observations before presenting 
these as a piece of academic work. Journals, diaries, profiles and portfolios 
are useful tools for collecting observation data. Rubrics and guides can be 
effective feedback tools."""), u"", u"reflection")
        self.emphasis         = Idevice.SomeEmphasis
        self.activity         = activity
        self.answer           = answer
        self._activityInstruc = x_(u"""Enter a question for learners 
to reflect upon.""")
        self._answerInstruc   = x_(u"""Describe how learners will assess how 
they have done in the exercise. (Rubrics are useful devices for providing 
reflective feedback.)""")
        self.systemResources += ["common.js"]
    activityInstruc = lateTranslate('activityInstruc')
    answerInstruc   = lateTranslate('answerInstruc')
    def upgradeToVersion1(self):
        """
        Upgrades the node from version 0 to 1.
        """
        log.debug(u"Upgrading iDevice")
        self.icon       = u"reflection"
    def upgradeToVersion2(self):
        """
        Upgrades the node from 1 (v0.5) to 2 (v0.6).
        Old packages will loose their icons, but they will load.
        """
        log.debug(u"Upgrading iDevice")
        self.emphasis = Idevice.SomeEmphasis
    def upgradeToVersion3(self):
        """
        Upgrades v0.6 to v0.7.
        """
        self.lastIdevice = False
    def upgradeToVersion4(self):
        """
        Upgrades to exe v0.10
        """
        self._upgradeIdeviceToVersion1()
        self._activityInstruc = self.__dict__['activityInstruc']
        self._answerInstruc   = self.__dict__['answerInstruc']
    def upgradeToVersion5(self):
        """
        Upgrades to exe v0.10
        """
        self._upgradeIdeviceToVersion1()
    def upgradeToVersion6(self):
        """
        Upgrades to v0.12
        """
        self._upgradeIdeviceToVersion2()
        self.systemResources += ["common.js"]
