import block

class Blockchain:
    '''
    This example class shows what our blockchain might look like.
    Does not deal with distribution of blockchain over a network or consensus issue
    '''
    def __init__(self):
        # genesisBlock is first block of the chain - can be hard coded
        self.genesisBlock = block.Block(1, '0', 'transactions are smart contracts')
        # store all blocks contained in that chain in a list (can use Hash Table etc. if necessary)
        self.chain = [self.genesisBlock]

    def getCurrentBlock(self):
        # last element in the list is the current block (most recently added)
        return self.chain[len(self.chain) - 1]

    def addBlock(self, transactions):
        # index of new block is incremented by 1 from previous block
        b = block.Block(self.getCurrentBlock().getIndex() + 1, self.getCurrentBlock().getHash(), transactions)
        # validate block before adding to chain
        if self.validateBlock(b):
            self.chain.append(b)
            return True
        return False

    def validateBlock(self, b):
        '''
        must validate blocks to detect if data in blocks has been changed
        can do this by checking if the stored hash is the same as the calculated
        hash for previous and current block.
        '''
        if b.getHash() != b.calculateHash():
            return False
        if b.getPreviousHash() != self.chain[b.getIndex() - 2].getHash() != self.chain[b.getIndex() - 2].calculateHash():
            return False
        return True

    def printBlockchain(self):
        print('\nPrinting Blockchain')
        for block in self.chain:
            block.printBlock()
