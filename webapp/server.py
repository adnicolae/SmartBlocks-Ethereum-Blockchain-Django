from twisted.internet.protocol import Factory, Protocol, ServerFactory, ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor

class BlockchainServerProtocol(LineReceiver):

    def lineReceived(self, line):
        print(line)

class BlockchainServerFactory(Factory):

    protocol = BlockchainServerProtocol

endpoint = TCP4ServerEndpoint(reactor, 64444)
endpoint.listen(BlockchainServerFactory())
reactor.run()
