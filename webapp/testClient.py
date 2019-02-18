from twisted.internet.protocol import Factory, Protocol, ServerFactory, ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor, defer

class SendBlockchainProtocol(Protocol):

    def sendContract(self, data):
        d = defer.Deferred()
        self.transport.write(data)
        return d

def sendJSON(p, data):
    print(data)
    d = p.sendContract(str.encode(data + '\r\n'))
    d.addCallback(lambda stop: reactor.stop())

jsonContract = "string"
endpoint = TCP4ClientEndpoint(reactor, "localhost", 64444)
connection = connectProtocol(endpoint, SendBlockchainProtocol())
connection.addCallback(sendJSON, jsonContract)
reactor.run(installSignalHandlers=0)
