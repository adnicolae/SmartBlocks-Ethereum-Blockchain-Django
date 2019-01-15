import block
import blockchain

# random example to test example blockchain/adding blocks to chain

testChain = blockchain.Blockchain()
testChain.printBlockchain()

testChain.addBlock('smart contract for car parts')
testChain.printBlockchain()

testChain.addBlock('smart contract for ...')
testChain.printBlockchain()
