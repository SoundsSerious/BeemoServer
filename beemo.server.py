# -*- coding: utf-8 -*-
"""
BEEMO: TWISTED DEV SERVER
"""
import os

from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver

PORT = 8330

os.chdir(os.path.dirname(os.path.realpath(__file__)))

class LoggingProtocol(LineReceiver):

    def lineReceived(self, line):
        self.factory.fp.write(line+'\n')


class LogfileFactory(Factory):

    protocol = LoggingProtocol

    def __init__(self, fileName):
        self.file = fileName

    def startFactory(self):
        self.fp = open(self.file, 'a')

    def stopFactory(self):
        self.fp.close()

if __name__ == '__main__':
    reactor.listenTCP(PORT,LogfileFactory('the~beemo~logs'))
    reactor.run()