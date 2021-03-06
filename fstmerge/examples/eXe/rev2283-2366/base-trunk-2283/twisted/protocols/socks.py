"""
Implementation of the SOCKSv4 protocol.
"""
from twisted.internet import reactor, protocol, defer
from twisted.python import log
import struct
import string
import socket
import time
class SOCKSv4Outgoing(protocol.Protocol):
    def __init__(self,socks):
        self.socks=socks
    def connectionMade(self):
        junk, host, port = self.transport.getPeer()
        self.socks.makeReply(90, 0, port=port, ip=host)
        self.socks.otherConn=self
    def connectionLost(self, reason):
        self.socks.transport.loseConnection()
    def dataReceived(self,data):
        self.socks.write(data)
    def write(self,data):
        self.socks.log(self,data)
        self.transport.write(data)
class SOCKSv4Incoming(protocol.Protocol):
    def __init__(self,socks):
        self.socks=socks
        self.socks.otherConn=self
    def connectionLost(self, reason):
        self.socks.transport.loseConnection()
    def dataReceived(self,data):
        self.socks.write(data)
    def write(self,data):
        self.socks.log(self,data)
        self.transport.write(data)
class SOCKSv4(protocol.Protocol):
    def __init__(self,logging=None):
        self.logging=logging
    def connectionMade(self):
        self.buf=""
        self.otherConn=None
    def dataReceived(self,data):
        if self.otherConn:
            self.otherConn.write(data)
            return
        self.buf=self.buf+data
        if '\000' in self.buf[8:]:
            head,self.buf=self.buf[:8],self.buf[8:]
            try:
                version,code,port=struct.unpack("!BBH",head[:4])
            except struct.error:
                raise RuntimeError, "struct error with head='%s' and buf='%s'"%(repr(head),repr(self.buf))
            user,self.buf=string.split(self.buf,"\000",1)
            if head[4:7]=="\000\000\000": # domain is after
                server,self.buf=string.split(self.buf,'\000',1)
            else:
                server=socket.inet_ntoa(head[4:8])
            assert version==4, "Bad version code: %s"%version
            if not self.authorize(code,server,port,user):
                self.makeReply(91)
                return
            if code==1: # CONNECT
                d = self.connectClass(server, port, SOCKSv4Outgoing, self)
                d.addErrback(lambda result, self=self: self.makeReply(91))
            elif code==2: # BIND
                ip = socket.gethostbyname(server)
                d = self.listenClass(0, SOCKSv4IncomingFactory, self, ip)
                d.addCallback(lambda (h, p), self=self: self.makeReply(90, 0, p, h))
            else:
                raise RuntimeError, "Bad Connect Code: %s" % code
            assert self.buf=="","hmm, still stuff in buffer... %s" % repr(self.buf)
    def connectionLost(self, reason):
        if self.otherConn:
            self.otherConn.transport.loseConnection()
    def authorize(self,code,server,port,user):
        log.msg("code %s connection to %s:%s (user %s) authorized" % (code,server,port,user))
        return 1
    def connectClass(self, host, port, klass, *args):
        return protocol.ClientCreator(reactor, klass, *args).connectTCP(host,port)
    def listenClass(self, port, klass, *args):
        serv = reactor.listenTCP(port, klass(*args))
        return defer.succeed(serv.getHost()[1:])
    def makeReply(self,reply,version=0,port=0,ip="0.0.0.0"):
        self.transport.write(struct.pack("!BBH",version,reply,port)+socket.inet_aton(ip))
        if reply!=90: self.transport.loseConnection()
    def write(self,data):
        self.log(self,data)
        self.transport.write(data)
    def log(self,proto,data):
        if not self.logging: return
        foo,ourhost,ourport=self.transport.getPeer()
        foo,theirhost,theirport=self.otherConn.transport.getPeer()
        f=open(self.logging,"a")
        f.write("%s\t%s:%d %s %s:%d\n"%(time.ctime(),
                                        ourhost,ourport,
                                        ((proto==self and '<') or '>'),
                                        theirhost,theirport))
        while data:
            p,data=data[:16],data[16:]
            f.write(string.join(map(lambda x:'%02X'%ord(x),p),' ')+' ')
            f.write((16-len(p))*3*' ')
            for c in p:
                if len(repr(c))>3: f.write('.')
                else: f.write(c)
            f.write('\n')
        f.write('\n')
        f.close()
class SOCKSv4Factory(protocol.Factory):
    """A factory for a SOCKSv4 proxy.
    Constructor accepts one argument, a logfile.
    """
    def __init__(self, log):
        self.logging = log
    def buildProtocol(self, addr):
        return SOCKSv4(self.logging)
class SOCKSv4IncomingFactory(protocol.Factory):
    """A utility class for building protocols for incoming connections."""
    def __init__(self, socks, ip):
        self.socks = socks
        self.ip = ip
    def buildProtocol(self, addr):
        if addr[0] == self.ip:
            self.ip = ""
            self.socks.makeReply(90, 0)
            return SOCKSv4Incoming(self.socks)
        elif self.ip == "":
            return None
        else:
            self.socks.makeReply(91, 0)
            self.ip = ""
            return None
