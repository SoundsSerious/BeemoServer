# -*- coding: utf-8 -*-
"""
BEEMO: TWISTED DEV SERVER
"""
import os,sys

from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.defer import Deferred
from twisted.python import log

PORT = 18330
HOST = 'frisbeem.local'
sdref = None


import pybonjour
from twisted.internet.interfaces import IReadDescriptor
from zope import interface

class MDNS_ServiceDescriptor(object):

    interface.implements(IReadDescriptor)

    def __init__(self, sdref):
        self.sdref = sdref

    def doRead(self):
        pybonjour.DNSServiceProcessResult(self.sdref)

    def fileno(self):
        return self.sdref.fileno()

    def logPrefix(self):
        return "bonjour"

    def connectionLost(self, reason):
        self.sdref.close()
        
        

def broadcast(reactor, regtype, port, name=None):
    def _callback(sdref, flags, errorCode, name, regtype, domain):
        if errorCode == pybonjour.kDNSServiceErr_NoError:
            d.callback((sdref, name, regtype, domain))
        else:
            d.errback(errorCode)

    d = Deferred()
    sdref = pybonjour.DNSServiceRegister(name = name,
                                        regtype = regtype,
                                        port = port,
                                        callBack = _callback)

    reactor.addReader(MDNS_ServiceDescriptor(sdref))
    return d
    

def broadcasting(args):
    global sdref
    sdref  = args[0]
    log.msg('Broadcasting %s.%s%s' % args[1:])

def failed(errorCode):
    log.err(errorCode)

class LoggingProtocol(LineReceiver):
    
    def __init__(self, factory):
        self.factory = factory
    
    def connectionMade(self):
        log.msg( 'Connection Made Sending Resp.' )
        self.sendLine("What's your name?")
        
    def lineReceived(self, line):
        log.msg( 'GOT:\t'+line )

class LogfileFactory(ReconnectingClientFactory):
    protocol = LoggingProtocol
    
    def startedConnecting(self, connector):
        print 'Started to connect.'

    def buildProtocol(self, addr):
        print 'Connected.'
        print 'Resetting reconnection delay'
        self.resetDelay()
        log.msg('Connected from {}'.format(addr) )        
        return self.protocol(self)

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason
        #ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        #ReconnectingClientFactory.clientConnectionFailed(self, connector,reason)
        connector.connect()
        

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))    
    
    print "starting rectors capin\'"
    reactor.connectTCP(HOST, PORT, LogfileFactory())
    
    print 'Opening Log'
    #log.startLogging(open('mdns_log.log', 'w'))
    log.startLogging( sys.stdout )
    
    print 'Starting MDNS Name Service'
    d = broadcast(reactor, "_beem._tcp", PORT, "beemo_dev")
    d.addCallback(broadcasting)
    d.addErrback(failed)
    
    reactor.run()