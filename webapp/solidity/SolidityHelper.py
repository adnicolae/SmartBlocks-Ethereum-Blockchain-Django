import time
from webapp.solidity import contract_abi
from web3 import Web3, HTTPProvider
from djutils.decorators import async
import hashlib, base64, datetime
from webapp.models import Asset, Record, User

# Address of deployed contract on the Ropsten Test Network
contract_address = '0xad61D6168Ec5218Aef4B60a2255F70232314adF0'
# Example user1 wallet setup
# wallet_private_key = 'C0A9D08F0AFFD022DCA3871301DDBDE6239E20DC3AD2B737E22816F5B189000C'
# wallet_address = '0xABD6618B45CF2325cA74e7781cC16D8AFc0c59fD'
# Example user2 wallet setup
# buyer_wallet_private_key = '6AE1CBFBC6BBCB6BCD3A6CA4B7C0E8F7D214F530802659A6937ED402ED82073D'
# buyer_wallet_address = '0x648C4D5eaE996345bE814BfAc4c79C5b848fb3a4'
# Example user3 wallet setup
user3_wallet_private_key = '1CED157C3A870514AEA6B2F04AA7DF7AD11C12B9EE2EE567590D7738E98F688C'
user3_wallet_address = '0xB58a431bc2BDc28042F1927C2c916022c4417314'
# Ropsten Ethereum Test Network Provider
w3 = Web3(HTTPProvider("https://ropsten.infura.io/v3/b54eec850dfc4954add7d0644a86ecee"))
w3.eth.enable_unaudited_features()
# Define contract object to work with
contract = w3.eth.contract(address=Web3.toChecksumAddress(contract_address), abi=contract_abi.abi)


# Get ether balance of an address
def getBalance(wallet_address):
    wei = w3.eth.getBalance(wallet_address)
    balance = w3.fromWei(wei, 'ether')
    return balance

# Generate a short hashcode
def generateId(assetName):
    asset = assetName + str(datetime.datetime.now())
    hasher = hashlib.sha1(asset.encode('utf-8'))
    encoded = base64.urlsafe_b64encode(hasher.digest()[:10])
    return encoded

@async
def create_asset(user_id, wallet_address, wallet_private_key, generatedId, name, description, price, stock, location, transfer_time, beneficiary_addresses, price_shares):
    nonce = w3.eth.getTransactionCount(wallet_address)

    txn_dict = contract.functions.createDigitalAsset(generatedId, name, description, price, stock, location, transfer_time, beneficiary_addresses, price_shares).buildTransaction({
        'chainId': 3,
        'gas': 800000,
        'gasPrice': w3.toWei('40', 'gwei'),
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=wallet_private_key)

    result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    tx_receipt = w3.eth.getTransactionReceipt(result)

    count = 0
    while tx_receipt is None and (count < 30):
        time.sleep(10)
        tx_receipt = w3.eth.getTransactionReceipt(result)
        print(tx_receipt)

    if tx_receipt is None:
        return {'status': 'failed', 'error': 'timeout'}

    processed_receipt = contract.events.AssetCreated().processReceipt(tx_receipt)
    print(processed_receipt)

    asset = Asset.objects.get(generatedId=generatedId)
    user = User.objects.get(id=user_id)

    if processed_receipt:
        argss = processed_receipt[0].args
        print(
            "Asset " + argss.name + " with address " + argss.assetAddress + " has been added to the network " + "and costs",
            argss._price, "wei per unit")
        asset.assetAddress = argss.assetAddress
        asset.transactionStatus = asset.SUCCESS
        user.wallet.ether_balance = getBalance(user.wallet.wallet_address)

        user.save()
    else:
        print("Added but failed")
        asset.transactionStatus = asset.FAIL

    asset.save()

    return {'status': 'added', 'processed_receipt': processed_receipt}

@async
def buy_asset(user_id, buyer_wallet_address, buyer_wallet_private_key, generatedId, amount_to_buy, recordId, amount_in_wei):
    #     amount_in_wei = w3.toWei(amount_in_ether,'ether');
    #     check if the amount inserted is the same as required

    nonce = w3.eth.getTransactionCount(buyer_wallet_address)

    txn_dict = contract.functions.buyAsset(generatedId, amount_to_buy, recordId).buildTransaction({
        'value': amount_in_wei,
        'chainId': 3,
        'gas': 8000000,
        'gasPrice': w3.toWei('40', 'gwei'),
        'nonce': nonce,
    })

    # Sign transaction with the wallet's private key
    signed_txn = w3.eth.account.signTransaction(txn_dict, buyer_wallet_private_key)

    # Send the transaction to the network
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    # Check if the transaction has been added to the blockchain by looking for a receipt
    txn_receipt = None
    count = 0
    while txn_receipt is None and (count < 30):
        txn_receipt = w3.eth.getTransactionReceipt(txn_hash)

        print(txn_receipt)

        time.sleep(10)

    if txn_receipt is None:
        return {'status': 'failed', 'error': 'timeout'}

    processed_receipt = contract.events.AssetTransfered().processReceipt(txn_receipt)
    print(processed_receipt)

    record = Record.objects.get(generatedId=recordId)
    asset = Asset.objects.get(generatedId=generatedId)
    buyer = User.objects.get(id=user_id)

    if processed_receipt:
        argss = processed_receipt[0].args
        print(
            "Record: " + argss.recordId + " of buyer " + argss.buyer + " of asset " + argss.asset)
        record.status = record.TRANSIT
        asset.stock = get_asset_stock(asset.assetAddress)
        buyer.wallet.ether_balance = getBalance(buyer.wallet.wallet_address)

        asset.save()
        buyer.save()
    else:
        print("Added but failed")
        record.status = record.TXFAILED

    record.save()

    return {'status': 'added', 'txn_receipt': txn_receipt, 'processed_receipt': processed_receipt}

@async
def confirm_asset(generatedId, amount_bought, recordId, amount_in_wei):
    #     amount_in_wei = w3.toWei(amount_in_ether,'ether');
    #     check if the amount inserted is the same as required

    nonce = w3.eth.getTransactionCount(buyer_wallet_address)

    txn_dict = contract.functions.confirmAsset(generatedId, amount_bought, recordId).buildTransaction({
        'value': amount_in_wei,
        'chainId': 3,
        'gas': 2000000,
        'gasPrice': w3.toWei('40', 'gwei'),
        'nonce': nonce,
    })

    # Sign transaction with the wallet's private key
    signed_txn = w3.eth.account.signTransaction(txn_dict, buyer_wallet_private_key)

    # Send the transaction to the network
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    # Check if the transaction has been added to the blockchain by looking for a receipt
    txn_receipt = None
    count = 0
    while txn_receipt is None and (count < 30):
        txn_receipt = w3.eth.getTransactionReceipt(txn_hash)

        print(txn_receipt)

        time.sleep(10)

    if txn_receipt is None:
        return {'status': 'failed', 'error': 'timeout'}

    processed_receipt = contract.events.TransactionCompleted().processReceipt(txn_receipt)
    print(processed_receipt)

    return {'status': 'added', 'txn_receipt': txn_receipt, 'processed_receipt': processed_receipt}

@async
def update_status(buyer, recordId, status):
    nonce = w3.eth.getTransactionCount(wallet_address)

    txn_dict = contract.functions.updateStatus(buyer, recordId, status).buildTransaction({
        'chainId': 3,
        'gas': 800000,
        'gasPrice': w3.toWei('40', 'gwei'),
        'nonce': nonce,
    })

    signed_txn = w3.eth.account.signTransaction(txn_dict, private_key=wallet_private_key)

    result = w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    tx_receipt = w3.eth.getTransactionReceipt(result)

    count = 0
    while tx_receipt is None and (count < 30):
        time.sleep(10)
        tx_receipt = w3.eth.getTransactionReceipt(result)
        print(tx_receipt)


    if tx_receipt is None:
        return {'status': 'failed', 'error': 'timeout'}

    return {'status': 'added', 'processed_receipt': tx_receipt}

def get_asset_stock(assetAddress):
    return contract.functions.getAssetAvailableStock(assetAddress).call()

def get_transaction_status(buyer, recordId):
    return contract.functions.getTransferStatus(buyer, recordId).call()

def get_amount_owed(buyer, recordId):
    return contract.functions.getAmountOwedFromRecord(buyer, recordId).call()