import datetime
import hashlib

class Block:

    def __init__(self, index, previousHash, contract, timestamp=None):
        # index of the current block
        self.index = index
        # hash of the previous block
        self.previousHash = previousHash
        # time (and date) the block was created
        if timestamp == None:
            self.timestamp = str(datetime.datetime.now())
        else:
            self.timestamp = timestamp
        self.contract = contract
        # hash of the current block
        self.currentHash = self.calculateHash()

    def getIndex(self):
        return self.index

    def getPreviousHash(self):
        return self.previousHash

    def getTimestamp(self):
        return self.timestamp

    def getContract(self):
        return self.contract

    def getHash(self):
        return self.currentHash

    def calculateHash(self):
        '''
        hash is calculated by concatenating the index, previous hash, timestamp and smart contract
        then, calculate hash of concatenated string
        '''
        h = hashlib.sha256()
        h.update((str(self.index) + self.previousHash + self.timestamp + self.contract).encode('ASCII'))
        return h.hexdigest()

    def printBlock(self):
        print('\n----------\n')
        print('Block ' + str(self.getIndex()) + ':')
        print('Timestamp: ' + self.getTimestamp())
        print('Contract: ' + self.getContract())
        print('Previous Hash: ' + self.getPreviousHash())
        print('Hash: ' + self.getHash())
        print('\n----------\n')
