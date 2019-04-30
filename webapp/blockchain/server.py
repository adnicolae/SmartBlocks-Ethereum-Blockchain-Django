import json
from blockchain import Blockchain
from block import Block
from twisted.internet.protocol import Factory, Protocol, ServerFactory, ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint, connectProtocol
from twisted.internet import reactor, task

class P2PServerProtocol(LineReceiver):

    def connectionMade(self):
        self.peer = self.transport.getPeer().host
        self.blockSender = False
        print('Connected to peer', self.peer)

    def connectionLost(self, reason):
        print('Disconnected from peer', self.peer)
        if self.peer == self.factory.lastPeer and self.blockSender == False:
            self.factory.lastPeer = self.factory.peers.pop(self.peer)
            print('Current Peers:')
            print(self.factory.peers)

    def lineReceived(self, line):
        message = json.loads(line.decode())
        if message['type'] == 'hello':
            self.handleHello()
        elif message['type'] == 'peer request':
            self.handlePeerRequest()
        elif message['type'] == 'disconnected':
            self.handleDisconnected()
        elif message['type'] == 'new contract':
            self.handleNewContract(message)
        elif message['type'] == 'vote':
            self.handleVote(message)

    def handleHello(self):
        if self.factory.state == 'READY':
            currentBlock = self.factory.blockchain.getCurrentBlock()
            self.sendCurrentBlock(currentBlock)
        else:
            self.transport.loseConnection()

    def sendCurrentBlock(self, currentBlock):
        message = json.dumps({'type': 'current block', 'index': str(currentBlock.getIndex()), 'previous hash': currentBlock.getPreviousHash(), 'timestamp': currentBlock.getTimestamp(), 'contract': currentBlock.getContract(), 'hash': currentBlock.getHash()})
        self.transport.write(str.encode(message + '\r\n'))

    def handlePeerRequest(self):
        if self.factory.state == 'READY':
            if self.peer not in self.factory.peers:
                self.factory.peers[self.peer] = self.factory.lastPeer
                self.factory.peerCons[self.peer] = self
                self.factory.lastPeer = self.peer
                print('Current Peers:')
                print(self.factory.peers)
                self.sendRequestedPeer(self.factory.peers[self.peer])
        else:
            self.transport.loseConnection()
    
    def sendRequestedPeer(self, peer):
        message = json.dumps({'type': 'requested peer', 'peer': peer})
        self.transport.write(str.encode(message + '\r\n'))

    def handleDisconnected(self):
        disconnectedPeer = self.factory.peers.pop(self.peer)
        self.factory.peerCons.pop(disconnectedPeer)
        newPeer = self.factory.peers.pop(disconnectedPeer)
        self.factory.peers[self.peer] = newPeer
        print('Current Peers:')
        print(self.factory.peers)
        self.sendNewPeer(newPeer)
        if self.factory.state == 'CONSENSUS' and disconnectedPeer not in self.factory.votesReceivedSet:
            self.factory.target -= 1
            if self.factory.replies['yes'] + self.factory.replies['no'] == self.factory.target:
                self.factory.resend.cancel()
                print('Cancelled')
                self.factory.consensus()

    def sendNewPeer(self, peer):
        message = json.dumps({'type': 'new peer', 'peer': peer})
        self.transport.write(str.encode(message + '\r\n'))

    def handleNewContract(self, message):
        if self.factory.state == 'READY':
            currentBlock = self.factory.blockchain.getCurrentBlock()
            contract = message['contract']
            self.factory.newBlock = Block(currentBlock.getIndex() + 1, currentBlock.getHash(), contract)
            self.factory.state = 'CONSENSUS'
            self.factory.resetConsensus()
            self.sendNewBlock(self.factory.newBlock)
        else:
            self.factory.contractsWaiting.append(message['contract'])
        self.blockSender = True
        self.transport.loseConnection()

    def sendNewBlock(self, newBlock):
        message = json.dumps({'type': 'new block', 'index': str(newBlock.getIndex()), 'previous hash': newBlock.getPreviousHash(), 'timestamp': newBlock.getTimestamp(), 'contract': newBlock.getContract(), 'hash': newBlock.getHash()})
        self.factory.peerCons[self.factory.lastPeer].transport.write(str.encode(message + '\r\n'))
        self.factory.resend = reactor.callLater(10, self.factory.resendNewBlock)

    def handleVote(self, message):
        if message['index'] != str(self.factory.newBlock.getIndex()) or self.factory.state != 'CONSENSUS':
            print('Vote Cancelled - old vote (' + self.peer + ')')
            return
        if self.factory.state == 'CONSENSUS':
            if self.factory.lastVoteReceived != None:
                if self.factory.peers[self.factory.lastVoteReceived] == self.peer:
                    self.tallyVote(message)
            elif self.peer == self.factory.lastPeer:
                self.tallyVote(message)
    
    def tallyVote(self, message):
        self.factory.votesReceived.add(self.peer)
        self.factory.lastVoteReceived = self.peer
        if message['vote'] == 'yes':
            self.factory.replies['yes'] += 1
        elif message['vote'] == 'no':
            self.factory.replies['no'] += 1
        if self.factory.replies['yes'] + self.factory.replies['no'] == self.factory.target:
            self.factory.resend.cancel()
            print('Cancelled')
            self.factory.consensus()

class P2PServerFactory(Factory):

    protocol = P2PServerProtocol

    def __init__(self):
        self.state = 'READY'
        self.blockchain = Blockchain()
        self.lastPeer = None
        self.peers = {}
        self.peerCons = {}
        self.contractsWaiting = []
        self.replies = {'yes': 0, 'no': 0}
        self.votesReceived = set()
        self.lastVoteReceived = None
        self.target = 0
        self.newBlock = None
        self.validateLoop = task.LoopingCall(self.blockchain.validateChain)
        self.validateLoop.start(10)

    def consensus(self):
        if self.replies['yes'] > self.target / 2:
            self.blockchain.addBlock(self.newBlock)
            message = json.dumps({'type': 'current block', 'index': str(self.newBlock.getIndex()), 'previous hash': self.newBlock.getPreviousHash(), 'timestamp': self.newBlock.getTimestamp(), 'contract': self.newBlock.getContract(), 'hash': self.newBlock.getHash()})
            for peer in self.peers:
                self.peerCons[peer].transport.write(str.encode(message + '\r\n'))
        if self.contractsWaiting:
            currentBlock = self.blockchain.getCurrentBlock()
            self.newBlock = Block(currentBlock.getIndex() + 1, currentBlock.getHash(), self.contractsWaiting.pop(0))
            self.resetConsensus()
            self.sendNewBlock()
        elif self.replies['yes'] + self.replies['no'] != self.target:
            self.resendNewBlock()
        else:
            print('READY')
            self.state = 'READY'

    def sendNewBlock(self):
        message = json.dumps({'type': 'new block', 'index': str(self.newBlock.getIndex()), 'previous hash': self.newBlock.getPreviousHash(), 'timestamp': self.newBlock.getTimestamp(), 'contract': self.newBlock.getContract(), 'hash': self.newBlock.getHash()})
        self.peerCons[self.lastPeer].transport.write(str.encode(message + '\r\n'))
        self.resend = reactor.callLater(10, self.resendNewBlock)

    def resendNewBlock(self):
        self.resetConsensus()
        self.sendNewBlock()
        print('Resent')

    def resetConsensus(self):
        self.replies['yes'] = 0
        self.replies['no'] = 0
        self.votesReceived = set()
        self.lastVoteReceived = None
        self.target = len(self.peers)

reactor.listenTCP(64444, P2PServerFactory())
reactor.run()
