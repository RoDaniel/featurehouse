"""
A Wikipedia Idevice is one built from a Wikipedia article.
"""
import re
from exe.engine.beautifulsoup import BeautifulSoup
from exe.engine.idevice       import Idevice
from exe.engine.field         import TextAreaField
from exe.engine.translate     import lateTranslate
from exe.engine.path          import Path, TempDirPath
from exe.engine.resource      import Resource
import urllib
class UrlOpener(urllib.FancyURLopener):
    """
    Set a distinctive User-Agent, so Wikipedia.org knows we're not spammers
    """
    version = "eXe/exe@auckland.ac.nz"
urllib._urlopener = UrlOpener()
import logging
log = logging.getLogger(__name__)
class WikipediaIdevice(Idevice):
    """
    A Wikipedia Idevice is one built from a Wikipedia article.
    """
    persistenceVersion = 8
    def __init__(self, defaultSite):
        Idevice.__init__(self, x_(u"Wiki Article"), 
                         x_(u"University of Auckland"), 
                         x_(u"""<p>The Wikipedia iDevice allows you to locate 
existing content from within Wikipedia and download this content into your eXe 
resource. The Wikipedia Article iDevice takes a snapshot copy of the article 
content. Changes in Wikipedia will not automatically update individual snapshot 
copies in eXe, a fresh copy of the article will need to be taken. Likewise, 
changes made in eXe will not be updated in Wikipedia. </p> <p>Wikipedia content 
is covered by the GNU free documentation license.</p>"""), 
                         u"", u"")
        self.emphasis         = Idevice.NoEmphasis
        self.articleName      = u""
        self.article          = TextAreaField(x_(u"Article"))
        self.article.idevice  = self
        self.images           = {}
        self.site             = defaultSite
        self.icon             = u"inter"
        self.systemResources += ["fdl.html"]
        self._langInstruc      = x_(u"""Select the appropriate language version 
of Wikipedia to search and enter search term.""")
        self._searchInstruc    = x_("""Enter a phrase or term you wish to search 
within Wikipedia.""")
        self.ownUrl               = ""
    langInstruc      = lateTranslate('langInstruc')
    searchInstruc    = lateTranslate('searchInstruc')
    def loadArticle(self, name):
        """
        Load the article from Wikipedia
        """
        self.articleName = name
        url = ""
        name = urllib.quote(name.replace(" ", "_").encode('utf-8'))
        try:
            url  = (self.site or self.ownUrl)
            if not url.endswith('/'): url += '/'
            if '://' not in url: url = 'http://' + url
            url += name
            net  = urllib.urlopen(url)
            page = net.read()
            net.close()
        except IOError, error:
            log.warning(unicode(error))
            self.article.content = _(u"Unable to download from %s <br/>Please check the spelling and connection and try again.") % url
            return
        soup = BeautifulSoup(unicode(page, "utf8"), False)
        content = soup.first('div', {'id': "content"})
        if not content:
            log.error("no content")
            self.article.content = _(u"Unable to download from %s <br/>Please check the spelling and connection and try again.") % url
            return
        while self.userResources:
            self.userResources[0].delete()
        self.images        = {}
        bits = url.split('/')
        netloc = '%s//%s' % (bits[0], bits[2])
        path = '/'.join(bits[3:-1])
        tmpDir = TempDirPath()
        for imageTag in content.fetch('img'):
            imageSrc  = unicode(imageTag['src'])
            imageName = imageSrc.split('/')[-1]
            if imageName not in self.images:
                if not imageSrc.startswith("http://"):
                    if imageSrc.startswith("/"):
                        imageSrc = netloc + imageSrc
                    else:
                        imageSrc = '%s/%s/%s' % (netloc, path, imageSrc)
                urllib.urlretrieve(imageSrc, tmpDir/imageName)
                self.images[imageName] = True
                Resource(self, tmpDir/imageName)
            imageTag['src'] = (u"/" + self.parentNode.package.name + u"/resources/" + imageName)
        self.article.content = self.reformatArticle(netloc, unicode(content))
    def reformatArticle(self, netloc, content):
        """
        Changes links, etc
        """
        content = re.sub(r'href="/', r'href="%s/' % netloc, content)
        content = re.sub(r'<div class="editsection".*?</div>', '', content)
        content = content.replace("\n", " ")
        content = re.sub(r'<script.*?</script>', '', content)
        return content
    def __getstate__(self):
        """
        Re-write the img URLs just in case the class name has changed
        """
        log.debug("in __getstate__ " + repr(self.parentNode))
        if self.parentNode:
            self.article.content = re.sub(r'/[^/]*?/resources/', 
                                          u"/" + self.parentNode.package.name + 
                                          u"/resources/", 
                                          self.article.content)
        return Idevice.__getstate__(self)
    def delete(self):
        """
        Clear out any old images when this iDevice is deleted
        """
        self.images = {}
        Idevice.delete(self)
    def upgradeToVersion1(self):
        """
        Called to upgrade from 0.6 release
        """
        self.site        = _('http://en.wikipedia.org/')
    def upgradeToVersion2(self):
        """
        Upgrades v0.6 to v0.7.
        """
        self.lastIdevice = False
    def upgradeToVersion3(self):
        """
        Upgrades exe to v0.10
        """
        self._upgradeIdeviceToVersion1()
        self._site = self.__dict__['site']
    def upgradeToVersion4(self):
        """
        Upgrades exe to v0.11... what was I thinking?
        """
        self.site = self.__dict__['_site']
    def upgradeToVersion5(self):
        """
        Upgrades exe to v0.11... forgot to change the icon
        """
        self.icon = u"inter"
    def upgradeToVersion6(self):
        """
        Upgrades to v0.12
        """
        self._upgradeIdeviceToVersion2()
        self.systemResources += ["fdl.html"]
        if self.images and self.parentNode:
            for image in self.images:
                imageResource = Resource(self, Path(image))
    def upgradeToVersion7(self):
        """
        Upgrades to v0.12
        """
        self._langInstruc   = x_(u"""Select the appropriate language version 
of Wikipedia to search and enter search term.""")
        self._searchInstruc = x_("""Enter a phrase or term you wish to search 
within Wikipedia.""")
    def upgradeToVersion8(self):
        """
        Upgrades to v0.19
        """
        self.ownUrl = ""
