import block

class Blockchain:

    def __init__(self, genesisBlock=None):
        # genesisBlock is first block of the chain - can be hard coded
        if genesisBlock == None:
            self.genesisBlock = block.Block(1, '0', 'Genesis Block')
        else:
            self.genesisBlock = genesisBlock
        # store all blocks contained in that chain in a list
        self.chain = [self.genesisBlock]

    def getCurrentBlock(self):
        # last element in the list is the current block (most recently added)
        return self.chain[len(self.chain) - 1]

    def addBlock(self, block):
        # append a new block to the end of the list
        self.chain.append(block)

    def validateBlock(self, b):
        '''
        must validate blocks to detect if data in blocks has been changed
        can do this by checking if the stored hash is the same as the calculated
        hash for previous and current block.
        '''
        if b.getIndex() != self.chain[b.getIndex() - 2].getIndex() + 1:
            return False
        if b.getHash() != b.calculateHash():
            return False
        if b.getPreviousHash() != self.chain[b.getIndex() - 2].getHash() != self.chain[b.getIndex() - 2].calculateHash():
            return False
        return True

    def validateChain(self):
        for i in range(1, len(self.chain)):
            if self.validateBlock(self.chain[i]) == False:
                return False
        print('Chain Validated')
        return True

    def printBlockchain(self):
        print('\nPrinting Blockchain')
        for block in self.chain:
            block.printBlock()
