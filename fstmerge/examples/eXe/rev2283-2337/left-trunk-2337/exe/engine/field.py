"""
Simple fields which can be used to build up a generic iDevice.
"""
import logging
from exe.engine.persist   import Persistable
from exe.engine.path      import Path
from exe.engine.resource  import Resource
from exe.engine.translate import lateTranslate
from exe.engine.mimetex   import compile
from HTMLParser           import HTMLParser
from exe.engine.flvreader import FLVReader
from htmlentitydefs       import name2codepoint
import re
import urllib
log = logging.getLogger(__name__)
class Field(Persistable):
    """
    A Generic iDevice is built up of these fields.  Each field can be
    rendered as an XHTML element
    """
    persistenceVersion = 1
    nextId = 1
    def __init__(self, name, instruc=""):
        """
        Initialize 
        """
        self._name     = name
        self._instruc  = instruc
        self._id       = Field.nextId
        Field.nextId  += 1
        self.idevice   = None
    name    = lateTranslate('name')
    instruc = lateTranslate('instruc')
    def getId(self):
        """
        Returns our id which is a combination of our iDevice's id
        and our own number.
        """
        if self.idevice:
            fieldId = self.idevice.id + "_"
        else:
            fieldId = ""
        fieldId += unicode(self._id)
        return fieldId
    id = property(getId)
    def upgradeToVersion1(self):
        """
        Upgrades to exe v0.10
        """
        self._name = self.__dict__['name']
        del self.__dict__['name']
        if self.__dict__.has_key('instruc'):
            self._instruc = self.__dict__['instruc']
        else:
            self._instruc = self.__dict__['instruction']
    def _upgradeFieldToVersion2(self):
        """
        Called from Idevices to upgrade fields to exe v0.12
        """
        pass
class TextField(Field):
    """
    A Generic iDevice is built up of these fields.  Each field can be
    rendered as an XHTML element
    """
    def __init__(self, name, instruc="", content=""):
        """
        Initialize 
        """
        Field.__init__(self, name, instruc)
        self.content = content
class TextAreaField(Field):
    """
    A Generic iDevice is built up of these fields.  Each field can be
    rendered as an XHTML element
    """
    def __init__(self, name, instruc="", content=""):
        """
        Initialize 
        """
        Field.__init__(self, name, instruc)
        self.content = content
class FeedbackField(Field):
    """
    A Generic iDevice is built up of these fields.  Each field can be
    rendered as an XHTML element
    """
    persistenceVersion = 1
    def __init__(self, name, instruc=""):
        """
        Initialize 
        """
        Field.__init__(self, name, instruc)
        self._buttonCaption = x_(u"Click Here")
        self.feedback      = ""
    buttonCaption = lateTranslate('buttonCaption')
    def upgradeToVersion1(self):
        """
        Upgrades to version 0.14
        """
        self.buttonCaption = self.__dict__['buttonCaption']
class ImageField(Field):
    """
    A Generic iDevice is built up of these fields.  Each field can be
    rendered as an XHTML element
    """
    def __init__(self, name, instruc=""):
        """
        """
        Field.__init__(self, name, instruc)
        self.width         = ""
        self.height        = ""
        self.imageResource = None
        self.defaultImage  = ""
    def setImage(self, imagePath):
        """
        Store the image in the package
        Needs to be in a package to work.
        """
        log.debug(u"setImage "+unicode(imagePath))
        resourceFile = Path(imagePath)
        assert(self.idevice.parentNode,
               'Image '+self.idevice.id+' has no parentNode')
        assert(self.idevice.parentNode.package,
               'iDevice '+self.idevice.parentNode.id+' has no package')
        if resourceFile.isfile():
            if self.imageResource:
                self.imageResource.delete()
            self.imageResource = Resource(self.idevice, resourceFile)
        else:
            log.error('File %s is not a file' % resourceFile)
    def setDefaultImage(self):
        """
        Set a default image to display until the user picks one
        """
        if self.defaultImage:
            self.setImage(self.defaultImage)
    def isDefault(self):
        """
        Returns true if the field holds it's default image
        """
        return self.imageResource.path == self.defaultImage
    def _upgradeFieldToVersion2(self):
        """
        Upgrades to exe v0.12
        """
        log.debug("ImageField upgrade field to version 2")
        if self.imageName and self.idevice.parentNode:
            self.imageResource = Resource(self.idevice, Path(self.imageName))
        else:
            self.imageResource = None
        del self.imageName
class MagnifierField(Field):
    """
    A Generic iDevice is built up of these fields.  Each field can be
    rendered as an XHTML element
    """
    def __init__(self, name, instruc=""):
        """
        """
        Field.__init__(self, name, instruc)
        self.width         = "100"
        self.height        = "100"
        self.imageResource = None
        self.defaultImage  = ""
        self.glassSize     = "2"
        self.initialZSize  = "100"
        self.maxZSize      = "150"
    def setImage(self, imagePath):
        """
        Store the image in the package
        Needs to be in a package to work.
        """
        log.debug(u"setImage "+unicode(imagePath))
        resourceFile = Path(imagePath)
        assert(self.idevice.parentNode,
               'Image '+self.idevice.id+' has no parentNode')
        assert(self.idevice.parentNode.package,
               'iDevice '+self.idevice.parentNode.id+' has no package')
        if resourceFile.isfile():
            if self.imageResource:
                self.imageResource.delete()
            self.imageResource = Resource(self.idevice, resourceFile)
        else:
            log.error('File %s is not a file' % resourceFile)
    def setDefaultImage(self):
        """
        Set a default image to display until the user picks one
        """
        if self.defaultImage:
            self.setImage(self.defaultImage)
class MultimediaField(Field):
    """
    A Generic iDevice is built up of these fields.  Each field can be
    rendered as an XHTML element
    """
    def __init__(self, name, instruc=""):
        """
        """
        Field.__init__(self, name, instruc)
        self.width         = "320"
        self.height        = "100"
        self.mediaResource = None
    def setMedia(self, mediaPath):
        """
        Store the media file in the package
        Needs to be in a package to work.
        """
        log.debug(u"setMedia "+unicode(mediaPath))
        resourceFile = Path(mediaPath)
        assert(self.idevice.parentNode,
               'Media '+self.idevice.id+' has no parentNode')
        assert(self.idevice.parentNode.package,
               'iDevice '+self.idevice.parentNode.id+' has no package')
        if resourceFile.isfile():
            if self.mediaResource:
                self.mediaResource.delete()
            self.mediaResource = Resource(self.idevice, resourceFile)
            if '+' in self.mediaResource.storageName:
                path = self.mediaResource.path
                newPath = path.replace('+','')
                Path(path).rename(newPath)
                self.mediaResource._storageName = \
                    self.mediaResource.storageName.replace('+','')
                self.mediaResource._path = newPath
        else:
            log.error('File %s is not a file' % resourceFile)
class ClozeHTMLParser(HTMLParser):
    """
    Separates out gaps from our raw cloze data
    """
    result = None
    inGap = False
    lastGap = ''
    lastText = ''
    whiteSpaceRe = re.compile(r'\s+')
    paragraphRe = re.compile(r'(\r\n\r\n)([^\r]*)(\1)')
    def reset(self):
        """
        Make our data ready
        """
        HTMLParser.reset(self)
        self.result = []
        self.inGap = False
        self.lastGap = ''
        self.lastText = ''
    def handle_starttag(self, tag, attrs):
        """
        Turn on inGap if necessary
        """
        if not self.inGap:
            if tag.lower() == 'u':
                self.inGap = True
            elif tag.lower() == 'span':
                attrs = dict(attrs)
                style = attrs.get('style', '')
                if 'underline' in style:
                    self.inGap = True
            elif tag.lower() == 'br':
                self.lastText += '<br/>' 
            else:
                self.writeTag(tag, attrs)
    def writeTag(self, tag, attrs=None):
        """
        Outputs a tag "as is"
        """
        if attrs is None:
            self.lastText += '</%s>' % tag
        else:
            attrs = ['"%s"="%s"' % (name, val) for name, val in attrs]
            if attrs:
                self.lastText += '<%s %s>' % (tag, ' '.join(attrs))
            else:
                self.lastText += '<%s>' % tag
    def handle_endtag(self, tag):
        """
        Turns of inGap
        """
        if self.inGap:
            if tag.lower() == 'u':
                self.inGap = False
                self._endGap()
            elif tag.lower() == 'span' and self.inGap:
                self.inGap = False
                self._endGap()
        elif tag.lower() != 'br':
            self.writeTag(tag)
    def _endGap(self):
        """
        Handles finding the end of gap
        """
        gapString = self.lastGap.strip()
        gapWords = self.whiteSpaceRe.split(gapString)
        gapSpacers = self.whiteSpaceRe.findall(gapString)
        if len(gapWords) > len(gapSpacers):
            gapSpacers.append(None)
        gaps = zip(gapWords, gapSpacers)
        lastText = self.lastText
        for gap, text in gaps:
            if gap == '<br/>':
                self.result.append((lastText, None))
            else:
                self.result.append((lastText, gap))
            lastText = text
        self.lastGap = ''
        self.lastText = ''
    def handle_data(self, data):
        """
        Adds the data to either lastGap or lastText
        """
        if self.inGap:
            self.lastGap += data
        else:
            self.lastText += data
    def close(self):
        """
        Fills in the last bit of result
        """
        if self.lastText:
            self._endGap()
        HTMLParser.close(self)
class ClozeField(Field):
    """
    This field handles a passage with words that the student must fill in
    """
    regex = re.compile('(%u)((\d|[A-F]){4})', re.UNICODE)
    persistenceVersion = 2
    def __init__(self, name, instruc):
        """
        Initialise
        """
        Field.__init__(self, name, instruc)
        self.parts = []
        self._encodedContent = ''
        self.rawContent = ''
        self._setVersion2Attributes()
    def _setVersion2Attributes(self):
        """
        Sets the attributes that were added in persistenceVersion 2
        """
        self.strictMarking = False
        self._strictMarkingInstruc = \
            x_(u"<p>If left unchecked a small number of spelling and "
                "capitalization errors will be accepted. If checked only "
                "an exact match in spelling and capitalization will be accepted."
                "</p>"
                "<p><strong>For example:</strong> If the correct answer is "
                "<code>Elephant</code> then both <code>elephant</code> and "
                "<code>Eliphant</code> will be judged "
                "<em>\"close enough\"</em> by the algorithm as it only has "
                "one letter wrong, even if \"Check Capitilization\" is on."
                "</p>"
                "<p>If capitalzation checking is off in the above example, "
                "the lowercase <code>e</code> will not be considered a "
                "mistake and <code>eliphant</code> will also be accepted."
                "</p>"
                "<p>If both \"Strict Marking\" and \"Check Capitilization\" "
                "are set, the only correct answer is \"Elephant\". If only "
                "\"Strict Marking\" is checked and \"Check Capitilization\" "
                "is not, \"elephant\" will also be accepted."
                "</p>")
        self.checkCaps = False
        self._checkCapsInstruc = \
            x_(u"<p>If this option is checked, submitted answers with "
                "different capitalization will be marked as incorrect."
                "</p>")
        self.instantMarking = False
        self._instantMarkingInstruc = \
            x_(u"""<p>If this option is set, each word will be marked as the 
learner types it rather then all the words being marked the end of the 
exercise.</p>""")
    def set_encodedContent(self, value):
        """
        Cleans out the encoded content as it is passed in. Makes clean XHTML.
        """
        for key, val in name2codepoint.items():
            value = value.replace('&%s;' % key, unichr(val))
        parser = ClozeHTMLParser()
        parser.feed(value)
        parser.close()
        self.parts = parser.result
        encodedContent = ''
        for shown, hidden in parser.result:
            encodedContent += shown
            if hidden:
                encodedContent += ' <u>'
                encodedContent += hidden
                encodedContent += '</u> ' 
        self._encodedContent = encodedContent
    encodedContent        = property(lambda self: self._encodedContent, 
                                     set_encodedContent)
    strictMarkingInstruc  = lateTranslate('strictMarkingInstruc')
    checkCapsInstruc      = lateTranslate('checkCapsInstruc')
    instantMarkingInstruc = lateTranslate('instantMarkingInstruc')
    def upgradeToVersion1(self):
        """
        Upgrades to exe v0.11
        """
        self.autoCompletion = True
        self.autoCompletionInstruc = _(u"""Allow auto completion when 
                                       user filling the gaps.""")
    def upgradeToVersion2(self):
        """
        Upgrades to exe v0.12
        """
        strictMarking = not self.autoCompletion
        del self.autoCompletion
        del self.autoCompletionInstruc
        self._setVersion2Attributes()
        self.strictMarking = strictMarking
class FlashField(Field):
    """
    A Generic iDevice is built up of these fields.  Each field can be
    rendered as an XHTML element
    """
    def __init__(self, name, instruc=""):
        """
        """
        Field.__init__(self, name, instruc)
        self.width         = 300
        self.height        = 250
        self.flashResource = None
        self._fileInstruc   = x_("""Only select .swf (Flash Objects) for 
this iDevice.""")
    fileInstruc = lateTranslate('fileInstruc')
    def setFlash(self, flashPath):
        """
        Store the image in the package
        Needs to be in a package to work.
        """
        log.debug(u"setFlash "+unicode(flashPath))
        resourceFile = Path(flashPath)
        assert(self.idevice.parentNode,
               'Flash '+self.idevice.id+' has no parentNode')
        assert(self.idevice.parentNode.package,
               'iDevice '+self.idevice.parentNode.id+' has no package')
        if resourceFile.isfile():
            if self.flashResource:
                self.flashResource.delete()
            self.flashResource = Resource(self.idevice, resourceFile)
        else:
            log.error('File %s is not a file' % resourceFile)
    def _upgradeFieldToVersion2(self):
        """
        Upgrades to exe v0.12
        """
        if hasattr(self, 'flashName'): 
            if self.flashName and self.idevice.parentNode:
                self.flashResource = Resource(self.idevice, Path(self.flashName))
            else:
                self.flashResource = None
            del self.flashName
    def _upgradeFieldToVersion3(self):
        """
        Upgrades to exe v0.13
        """
        self._fileInstruc   = x_("""Only select .swf (Flash Objects) for 
this iDevice.""")
class FlashMovieField(Field):
    """
    A Generic iDevice is built up of these fields.  Each field can be
    rendered as an XHTML element
    """
    def __init__(self, name, instruc=""):
        """
        """
        Field.__init__(self, name, instruc)
        self.width         = 300
        self.height        = 250
        self.flashResource = None
        self._fileInstruc   = x_("""Only select .flv (Flash Video Files) for 
this iDevice.""")
    fileInstruc = lateTranslate('fileInstruc')
    def setFlash(self, flashPath):
        """
        Store the image in the package
        Needs to be in a package to work.
        """
        log.debug(u"setFlash "+unicode(flashPath))
        resourceFile = Path(flashPath)
        assert(self.idevice.parentNode,
               'Flash '+self.idevice.id+' has no parentNode')
        assert(self.idevice.parentNode.package,
               'iDevice '+self.idevice.parentNode.id+' has no package')
        if resourceFile.isfile():
            if self.flashResource:
                self.flashResource.delete()
            try:
                flvDic = FLVReader(resourceFile)
                self.height = flvDic["height"] +30        
                self.width  = flvDic["width"]
                self.flashResource = Resource(self.idevice, resourceFile)
            except AssertionError: 
                log.error('File %s is not a flash movie' % resourceFile)
        else:
            log.error('File %s is not a file' % resourceFile)
    def _upgradeFieldToVersion2(self):
        """
        Upgrades to exe v0.12
        """
        if hasattr(self, 'flashName'):
            if self.flashName and self.idevice.parentNode:
                self.flashResource = Resource(self.idevice, Path(self.flashName))
            else:
                self.flashResource = None
            del self.flashName
    def _upgradeFieldToVersion3(self):
        """
        Upgrades to exe v0.14
        """
        self._fileInstruc   = x_("""Only select .flv (Flash Video Files) for 
this iDevice.""")
class DiscussionField(Field):
    def __init__(self, name, instruc=x_("Type a discussion topic here."), content="" ):
        """
        Initialize 
        """
        Field.__init__(self, name, instruc)
        self.content = content
class MathField(Field):
    """
    A Generic iDevice is built up of these fields.  Each field can be
    rendered as an XHTML element
    """
    persistenceVersion = 1
    def __init__(self, name, instruc="", latex=""):
        """
        Initialize 
        'self._latex' is a string of latex
        'self.gifResource' is a resouce that points to a cached gif
        rendered from the latex
        """
        Field.__init__(self, name, instruc)
        self._latex      = latex # The latex entered by the user
        self.gifResource = None
        self.fontsize = 4
        self.instruc     = x_(u""
        "<p>" 
        "Select symbols from the text editor below or enter LATEX manually"
        " to create mathematical formula."
        " To preview your LATEX as it will display use the &lt;Preview&gt;"
        " button below.")
        "</p>"
        self._previewInstruc = x_("""Click on Preview button to convert 
                                  the latex into an image.""")
    def get_latex(self):
        """
        Returns latex string
        """
        return self._latex
    def set_latex(self, latex):
        """
        Replaces current gifResource
        """
        if self.gifResource is not None:
            self.gifResource.delete()
            self.gifResource = None
        if latex <> "":
            tempFileName = compile(latex, self.fontsize)
            self.gifResource = Resource(self.idevice, tempFileName)
            Path(tempFileName).remove()
        self._latex = latex
    def get_gifURL(self):
        """
        Returns the url to our gif for putting inside
        <img src=""/> tag attributes
        """
        if self.gifResource is None:
            return ''
        else:
            return self.gifResource.path
    def _upgradeFieldToVersion1(self):
        """
        Upgrades to exe v0.19
        """
        self.fontsize = "4"
    latex = property(get_latex, set_latex)
    gifURL = property(get_gifURL)
    previewInstruc = lateTranslate('previewInstruc')
class QuizOptionField(Field):
    """
    A Question is built up of question and options.  Each
    option can be rendered as an XHTML element
    """
    def __init__(self, name="", instruc=""):
        """
        Initialize 
        """
        Field.__init__(self, name, instruc)
        self.idevice   = None
        self.question  = None
        self.answer    = ""
        self.isCorrect = False
        self.feedback  = ""
class QuizQuestionField(Field):
    """
    A Question is built up of question and Options.
    """
    def __init__(self, name, instruc=""):
        """
        Initialize 
        """
        Field.__init__(self, name, instruc)
        self.question             = ""
        self.hint                 = ""
        self.options              = []
    def addOption(self):
        """
        Add a new option to this question. 
        """
        option = QuizOptionField()
        option.question = self
        option.idevice  = self.idevice
        self.options.append(option)
class SelectOptionField(Field):
    """
    A Question is built up of question and options.  Each
    option can be rendered as an XHTML element
    """
    def __init__(self, name="", instruc=""):
        """
        Initialize 
        """
        Field.__init__(self, name, instruc)
        self.idevice   = None
        self.question  = None
        self.answer    = ""
        self.isCorrect = False
class SelectQuestionField(Field):
    """
    A Question is built up of question and Options.
    """
    def __init__(self, name, instruc=""):
        """
        Initialize 
        """
        Field.__init__(self, name, instruc)
        self.question             = ""
        self.options              = []
        self._questionInstruc      = x_(u"""Enter the question stem. 
The quest should be clear and unambiguous. Avoid negative premises 
as these can tend to be ambiguous.""")
        self._optionInstruc        = x_(u"""Enter an answer option. Provide 
a range of plausible distractors (usually 3-4) as well as the correct answer. 
Click on the &lt;Add another option&gt; button to add another answer.""")
        self._correctAnswerInstruc = x_(u"""To indicate the correct answer, 
click the radio button next to the correct option.""")
        self.feedback              = ""
        self.feedbackInstruc       = ""
    questionInstruc      = lateTranslate('questionInstruc')
    optionInstruc        = lateTranslate('optionInstruc')
    correctAnswerInstruc = lateTranslate('correctAnswerInstruc')
    def addOption(self):
        """
        Add a new option to this question. 
        """
        option = SelectOptionField()
        option.question = self
        option.idevice  = self.idevice
        self.options.append(option)
