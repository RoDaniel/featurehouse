from xml.sax import make_parser, handler
import xml as pyxml
from nevow.stan import xml, Tag, directive, slot
import nevow
try:
    bad_version = pyxml.version_info < (0,8,2)
    bad_startdtd_args = pyxml.version_info < (0,8,3)
except:
    import sys
    bad_version = sys.version_info < (2,3)
    bad_startdtd_args = sys.version_info < (2,4)
class nscontext(object):
    def __init__(self, parent=None):
        self.parent = parent
        if parent is not None:
            self.nss = dict(parent.nss)
        else:
            self.nss = {'http://www.w3.org/XML/1998/namespace':'xml'}
    def get(self, k, d=None):
        return self.nss.get(k, d)
    def __setitem__(self, k, v):
        self.nss.__setitem__(k, v)
    def __getitem__(self, k):
        return self.nss.__getitem__(k)
class ToStan(handler.ContentHandler, handler.EntityResolver):
    directiveMapping = {
        'render': 'render',
        'data': 'data',
        'macro': 'macro',
    }
    attributeList = [
        'pattern', 'key',
    ]
    def __init__(self, ignoreDocType, ignoreComment):
        self.ignoreDocType = ignoreDocType
        self.ignoreComment = ignoreComment
        self.prefixMap = nscontext()
        self.inCDATA = False
    def resolveEntity(self, publicId, systemId):
        raise Exception("resolveEntity should not be called. We don't use external DTDs.")
    def skippedEntity(self, name):
        self.current.append(xml("&%s;"%name))
    def startDocument(self):
        self.document = []
        self.current = self.document
        self.stack = []
        self.xmlnsAttrs = []
    def endDocument(self):
        pass
    def processingInstruction(self, target, data):
        self.current.append(xml("<?%s %s?>\n" % (target, data)))
    def startPrefixMapping(self, prefix, uri):
        self.prefixMap = nscontext(self.prefixMap)
        self.prefixMap[uri] = prefix
        if uri == nevow.namespace:
            return
        if prefix is None:
            self.xmlnsAttrs.append(('xmlns',uri))
        else:
            self.xmlnsAttrs.append(('xmlns:%s'%prefix,uri))
    def endPrefixMapping(self, prefix):
        self.prefixMap = self.prefixMap.parent
    def startElementNS(self, ns_and_name, qname, attrs):
        ns, name = ns_and_name
        if ns == nevow.namespace:
            if name == 'invisible':
                name = ''
            elif name == 'slot':
                el = slot(attrs[(None,'name')])
                self.stack.append(el)
                self.current.append(el)
                self.current = el.children
                return
        attrs = dict(attrs)
        specials = {}
        attributes = self.attributeList
        directives = self.directiveMapping
        for k, v in attrs.items():
            att_ns, nons = k
            if att_ns != nevow.namespace:
                continue
            if nons in directives:
                specials[directives[nons]] = directive(v)
                del attrs[k]
            if nons in attributes:
                specials[nons] = v
                del attrs[k]
        no_ns_attrs = {}
        for (attrNs, attrName), v in attrs.items():
            nsPrefix = self.prefixMap.get(attrNs)
            if nsPrefix is None:
                no_ns_attrs[attrName] = v
            else:
                no_ns_attrs['%s:%s'%(nsPrefix,attrName)] = v
        if ns == nevow.namespace and name == 'attr':
            if not self.stack:
                raise AssertionError( '<nevow:attr> as top-level element' )
            if 'name' not in no_ns_attrs:
                raise AssertionError( '<nevow:attr> requires a name attribute' )
            el = Tag('', specials=specials)
            self.stack[-1].attributes[no_ns_attrs['name']] = el
            self.stack.append(el)
            self.current = el.children
            return
        if self.xmlnsAttrs:
            no_ns_attrs.update(dict(self.xmlnsAttrs))
            self.xmlnsAttrs = []
        el = Tag(name, attributes=dict(no_ns_attrs), specials=specials)
        self.stack.append(el)
        self.current.append(el)
        self.current = el.children
    def characters(self, ch):
        if self.inCDATA:
            ch = xml(ch)
        self.current.append(ch)
    def endElementNS(self, name, qname):
        me = self.stack.pop()
        if self.stack:
            self.current = self.stack[-1].children
        else:
            self.current = self.document
    def startDTD(self, name, publicId, systemId):
        if self.ignoreDocType:
            return
        if bad_startdtd_args:
            systemId, publicId = publicId, systemId
        doctype = '<!DOCTYPE %s\n  PUBLIC "%s"\n  "%s">\n' % (name, publicId, systemId)
        self.current.append(xml(doctype))
    def endDTD(self, *args):
        pass
    def startCDATA(self):
        self.inCDATA = True
        self.current.append(xml('<![CDATA['))
    def endCDATA(self):
        self.inCDATA = False
        self.current.append(xml(']]>'))
    def comment(self, content):
        if self.ignoreComment:
            return
        self.current.append( (xml('<!-- '),xml(content),xml(' -->')) )
def parse(fl, ignoreDocType=False, ignoreComment=False):
    if bad_version:
        raise Exception("Please use PyXML later than 0.8.2 or python later than 2.3. Earlier ones are too buggy.")
    parser = make_parser()
    parser.setFeature(handler.feature_validation, 0)
    parser.setFeature(handler.feature_namespaces, 1)
    parser.setFeature(handler.feature_external_ges, 0)
    parser.setFeature(handler.feature_external_pes, 0)
    s = ToStan(ignoreDocType, ignoreComment)
    parser.setContentHandler(s)
    parser.setEntityResolver(s)
    parser.setProperty(handler.property_lexical_handler, s)
    parser.parse(fl)
    return s.document
def parseString(t, ignoreDocType=False, ignoreComment=False):
    from cStringIO import StringIO
    return parse(StringIO(t), ignoreDocType, ignoreComment)
