import json
from blockchain import Blockchain
from block import Block
from twisted.internet.protocol import Factory, Protocol, ServerFactory, ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor

class SendBlockProtocol(Protocol):

    def connectionMade(self):
        message = json.dumps({'type': 'new contract', 'contract': self.factory.block})
        self.transport.write(str.encode(message + '\r\n'))

    def connectionLost(self, reason):
        #reactor.stop()


class SendBlockFactory(ClientFactory):

    protocol = SendBlockProtocol

    def __init__(self, block):
        self.block = block

def send(contract):
    reactor.connectTCP('localhost', 64444, SendBlockFactory(contract))
    if not reactor.running:
        reactor.run()


