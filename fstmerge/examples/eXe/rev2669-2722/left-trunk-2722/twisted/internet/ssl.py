"""SSL transport. Requires PyOpenSSL (http://pyopenssl.sf.net).
SSL connections require a ContextFactory so they can create SSL contexts.
End users should only use the ContextFactory classes directly - for SSL
connections use the reactor.connectSSL/listenSSL and so on, as documented
in IReactorSSL.
All server context factories should inherit from ContextFactory, and all
client context factories should inherit from ClientContextFactory. At the
moment this is not enforced, but in the future it might be.
API Stability: stable
Future Plans:
    - split module so reactor-specific classes are in a separate module
    - support for switching TCP into SSL
    - more options
Maintainer: U{Itamar Shtull-Trauring<mailto:twisted@itamarst.org>}
"""
supported = False
from OpenSSL import SSL
import socket
from zope.interface import implements, implementsOnly, implementedBy
import tcp, interfaces
from twisted.python import log, components
from twisted.internet import base, address
class ContextFactory:
    """A factory for SSL context objects, for server SSL connections."""
    isClient = 0
    def getContext(self):
        """Return a SSL.Context object. override in subclasses."""
        raise NotImplementedError
class DefaultOpenSSLContextFactory(ContextFactory):
    def __init__(self, privateKeyFileName, certificateFileName,
                 sslmethod=SSL.SSLv23_METHOD):
        """
        @param privateKeyFileName: Name of a file containing a private key
        @param certificateFileName: Name of a file containing a certificate
        @param sslmethod: The SSL method to use
        """
        self.privateKeyFileName = privateKeyFileName
        self.certificateFileName = certificateFileName
        self.sslmethod = sslmethod
        self.cacheContext()
    def cacheContext(self):
        ctx = SSL.Context(self.sslmethod)
        ctx.use_certificate_file(self.certificateFileName)
        ctx.use_privatekey_file(self.privateKeyFileName)
        self._context = ctx
    def __getstate__(self):
        d = self.__dict__.copy()
        del d['_context']
        return d
    def __setstate__(self, state):
        self.__dict__ = state
        self.cacheContext()
    def getContext(self):
        """Create an SSL context.
        """
        return self._context
class ClientContextFactory:
    """A context factory for SSL clients."""
    isClient = 1
    method = SSL.SSLv3_METHOD
    def getContext(self):
        return SSL.Context(self.method)
class Client(tcp.Client):
    """I am an SSL client."""
    implementsOnly(interfaces.ISSLTransport,
                   *[i for i in implementedBy(tcp.Client) if i != interfaces.ITLSTransport])
    def __init__(self, host, port, bindAddress, ctxFactory, connector, reactor=None):
        self.ctxFactory = ctxFactory
        tcp.Client.__init__(self, host, port, bindAddress, connector, reactor)
    def getHost(self):
        """Returns the address from which I am connecting."""
        h, p = self.socket.getsockname()
        return address.IPv4Address('TCP', h, p, 'SSL')
    def getPeer(self):
        """Returns the address that I am connected."""
        return address.IPv4Address('TCP', self.addr[0], self.addr[1], 'SSL')
    def _connectDone(self):
        self.startTLS(self.ctxFactory)
        self.startWriting()
        tcp.Client._connectDone(self)
components.backwardsCompatImplements(Client)
class Server(tcp.Server):
    """I am an SSL server.
    """
    implements(interfaces.ISSLTransport)
    def getHost(self):
        """Return server's address."""
        h, p = self.socket.getsockname()
        return address.IPv4Address('TCP', h, p, 'SSL')
    def getPeer(self):
        """Return address of peer."""
        h, p = self.client
        return address.IPv4Address('TCP', h, p, 'SSL')
components.backwardsCompatImplements(Server)
class Port(tcp.Port):
    """I am an SSL port."""
    _socketShutdownMethod = 'sock_shutdown'
    transport = Server
    def __init__(self, port, factory, ctxFactory, backlog=50, interface='', reactor=None):
        tcp.Port.__init__(self, port, factory, backlog, interface, reactor)
        self.ctxFactory = ctxFactory
    def createInternetSocket(self):
        """(internal) create an SSL socket
        """
        sock = tcp.Port.createInternetSocket(self)
        return SSL.Connection(self.ctxFactory.getContext(), sock)
    def _preMakeConnection(self, transport):
        transport._startTLS()
        return tcp.Port._preMakeConnection(self, transport)
class Connector(base.BaseConnector):
    def __init__(self, host, port, factory, contextFactory, timeout, bindAddress, reactor=None):
        self.host = host
        self.port = port
        self.bindAddress = bindAddress
        self.contextFactory = contextFactory
        base.BaseConnector.__init__(self, factory, timeout, reactor)
    def _makeTransport(self):
        return Client(self.host, self.port, self.bindAddress, self.contextFactory, self, self.reactor)
    def getDestination(self):
        return address.IPv4Address('TCP', self.host, self.port, 'SSL')
__all__ = ["ContextFactory", "DefaultOpenSSLContextFactory", "ClientContextFactory"]
supported = True
