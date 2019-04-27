import json
import time
from block import Block
from twisted.internet.protocol import Factory, Protocol, ServerFactory, ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor, defer, task

class ConnectServerProtocol(LineReceiver):

    def connectionMade(self):
        print('Connected to server', self.transport.getPeer().host)
        if self.factory.state == 'START':
            self.sendHello()

    def connectionLost(self, reason):
        print('Disconnected from server')

    def lineReceived(self, line):
        message = json.loads(line.decode())
        if message['type'] == 'current block':
            self.handleCurrentBlock(message)
        elif message['type'] == 'requested peer':
            self.handleRequestedPeer(message)
        elif message['type'] == 'new peer':
            self.handleNewPeer(message)
        elif message['type'] == 'new block':
            self.handleNewBlock(message)

    def sendHello(self):
        message = json.dumps({'type': 'hello'})
        self.transport.write(str.encode(message + '\r\n'))

    def handleCurrentBlock(self, message):
        self.factory.currentBlock = Block(int(message['index']), message['previous hash'], message['contract'], message['timestamp'])
        print('Current Block:')
        self.factory.currentBlock.printBlock()
        if self.factory.state == 'START':
            self.sendPeerRequest()

    def sendPeerRequest(self):
        message = json.dumps({'type': 'peer request'})
        self.transport.write(str.encode(message + '\r\n'))

    def handleRequestedPeer(self, message):
        print('Listening for peers')
        reactor.listenTCP(60000, ListenPeerFactory(self))
        if message['peer'] != None:
            reactor.connectTCP(message['peer'], 60000, ConnectPeerFactory(self))
        self.factory.state = 'CONNECTED'

    def handleNewPeer(self, message):
        if message['peer'] != None:
            reactor.connectTCP(message['peer'], 60000, ConnectPeerFactory(self))

    def handleNewBlock(self, message):
        newBlock = Block(int(message['index']), message['previous hash'], message['contract'], message['timestamp'])
        if int(message['index']) != self.factory.currentBlock.getIndex() + 1:
            self.sendVote('no', message)
            return False
        if message['previous hash'] != self.factory.currentBlock.getHash() != self.factory.currentBlock.calculateHash():
            self.sendVote('no', message)
            return False
        if message['hash'] != newBlock.getHash() != newBlock.calculateHash():
            self.sendVote('no', message)
            return False
        self.sendVote('yes', message)
        return True

    def sendVote(self, vote, blockMessage):
        message = json.dumps({'type': 'vote', 'vote': vote, 'index': blockMessage['index']})
        self.transport.write(str.encode(message + '\r\n'))
        if self.factory.peerCon != None:
            message = json.dumps({'type': 'new block', 'index': blockMessage['index'], 'previous hash': blockMessage['previous hash'], 'timestamp': blockMessage['timestamp'], 'contract': blockMessage['contract'], 'hash': blockMessage['hash']})
            self.factory.peerCon.transport.write(str.encode(message + '\r\n'))

class ConnectServerFactory(ClientFactory):

    protocol = ConnectServerProtocol

    def __init__(self):
        self.state = 'START'
        self.peerCon = None
        self.currentBlock = None

class ListenPeerProtocol(LineReceiver):

    def connectionMade(self):
        self.peer = self.transport.getPeer().host
        print('Connected to peer', self.peer, 'as server')

    def connectionLost(self, reason):
        print('Disconnected from peer', self.peer, 'as server')

    def lineReceived(self, line):
        message = json.loads(line.decode())
        if message['type'] == 'new block':
            self.handleNewBlock(message)

    def handleNewBlock(self, message):
        newBlock = Block(int(message['index']), message['previous hash'], message['contract'], message['timestamp'])
        if int(message['index']) != self.factory.getServerConnection().factory.currentBlock.getIndex() + 1:
            self.sendVote('no', message)
            return False
        if message['previous hash'] != self.factory.getServerConnection().factory.currentBlock.getHash() != self.factory.getServerConnection().factory.currentBlock.calculateHash():
            self.sendVote('no', message)
            return False
        if message['hash'] != newBlock.getHash() != newBlock.calculateHash():
            self.sendVote('no', message)
            return False
        self.sendVote('yes', message)
        return True

    def sendVote(self, vote, blockMessage):
        message = json.dumps({'type': 'vote', 'vote': vote, 'index': blockMessage['index']})
        self.factory.getServerConnection().transport.write(str.encode(message + '\r\n'))
        if self.factory.getServerConnection().factory.peerCon != None:
            message = json.dumps({'type': 'new block', 'index': blockMessage['index'], 'previous hash': blockMessage['previous hash'], 'timestamp': blockMessage['timestamp'], 'contract': blockMessage['contract'], 'hash': blockMessage['hash']})
            self.factory.getServerConnection().factory.peerCon.transport.write(str.encode(message + '\r\n'))

class ListenPeerFactory(ServerFactory):

    protocol = ListenPeerProtocol

    def __init__(self, con):
        self.con = con

    def getServerConnection(self):
        return self.con

class ConnectPeerProtocol(LineReceiver):

    def connectionMade(self):
        self.factory.getServerConnection().factory.peerCon = self
        self.peer = self.transport.getPeer().host
        print('Connected to peer', self.peer, 'as client')

    def connectionLost(self, reason):
        print('Disconnected from peer', self.peer, 'as client')
        message = json.dumps({'type': 'disconnected'})
        self.factory.getServerConnection().transport.write(str.encode(message + '\r\n'))

class ConnectPeerFactory(ClientFactory):

    protocol = ConnectPeerProtocol

    def __init__(self, con):
        self.con = con

    def getServerConnection(self):
        return self.con

reactor.connectTCP('137.205.112.136', 64444, ConnectServerFactory())
reactor.run()
