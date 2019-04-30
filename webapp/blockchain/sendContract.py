import json
from .blockchain import Blockchain
from .block import Block
from twisted.internet.protocol import Factory, Protocol, ServerFactory, ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor

class SendContractProtocol(Protocol):

    def connectionMade(self):
        # send message containing contract, encrypted contracts and public keys
        # this is sent from the webapp
        message = json.dumps({'type': 'new contract', 'contract': self.factory.contract, 'buyer key': self.factory.buyerKey.decode(), 'seller key': self.factory.sellerKey.decode(),
        'buyer cipher': self.factory.buyerCipher.decode('raw_unicode_escape'), 'seller cipher': self.factory.sellerCipher.decode('raw_unicode_escape')})
        self.transport.write(str.encode(message + '\r\n'))
        self.transport.loseConnection()

    def connectionLost(self, reason):
        reactor.crash()


class SendContractFactory(ClientFactory):

    protocol = SendContractProtocol

    def __init__(self, contract, buyerKey, sellerKey, buyerCipher, sellerCipher):
        self.contract = contract
        self.buyerKey = buyerKey
        self.sellerKey = sellerKey
        self.buyerCipher = buyerCipher
        self.sellerCipher = sellerCipher

def send(contract, buyerKey, sellerKey, buyerCipher, sellerCipher):
    '''
    function is called from webapp
    connect to server on port 64444
    replace 'localhost' with server IP
    when server not running on local machine

    USE OF LOCAL IP ADDRESSES WILL WORK (192.168 etc.)
    USE OF PUBLIC IP ADDRESSES WILL REQUIRE PORT FORWARDING
    ON PORTS 64444 and 60000
    '''
    reactor.connectTCP('localhost', 64444, SendContractFactory(contract, buyerKey, sellerKey, buyerCipher, sellerCipher))
    if not reactor.running:
        reactor.run(installSignalHandlers=0)


