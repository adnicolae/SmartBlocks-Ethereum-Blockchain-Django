pragma solidity ^0.4.10;


contract Owned {

  address owner;

  modifier onlyOwner {
    require(msg.sender == owner);
    _;
  }
}


contract Mortal is Owned {
  function remove() onlyOwner {
    selfdestruct(owner);
  }
}

/*
    Contract to model an asset manager.
*/
contract DigitalAsset is Mortal {
    string generatedId;
    string description;
    uint price;
    uint stock;
    uint transferTime;
    Beneficiary[] beneficiaries;
    uint totalBeneficiaryPercentage;

    // event AssetCreated(string _description, uint _price,
    // uint _stock, string _location, uint _transferTime, address[] _beneficiaryAddresses, uint[] _priceShare);

    function DigitalAsset(string _generatedId, string _description, uint _price,
    uint _stock, uint _transferTime, address[] _beneficiaryAddresses, uint[] _priceShare) {
        owner = msg.sender;
        generatedId = _generatedId;
        description = _description;
        price = _price;
        stock = _stock;
        transferTime = _transferTime;


        uint beneficiaryCount = _beneficiaryAddresses.length;
        for (uint i = 0; i < beneficiaryCount; i++) {
            uint percentage = _priceShare[i];

            pushBeneficiary(_beneficiaryAddresses[i], percentage);
            totalBeneficiaryPercentage += percentage;
        }

        // AssetCreated(_description, _price, _stock, _location, _transferTime, _beneficiaryAddresses, _priceShare);
    }

    function getPrice() constant returns (uint) {
        return price;
    }

    function getExistingStock() constant returns (uint) {
        return stock;
    }


    function updateExistingStock(uint amount) {
        stock -= amount;
    }

    function addStock(uint amount) {
        stock += amount;
    }

    event BeneficiaryPaid(address addr, uint amount);

    function payBeneficiaries(uint amountOwed) payable onlyOwner {
        require(msg.value >= amountOwed);

        uint beneficiaryCount = beneficiaries.length;
        for (uint i = 0; i < beneficiaryCount; i++) {
            Beneficiary memory beneficiary = beneficiaries[i];

            uint percentage = beneficiary.priceShare;
            address addr = beneficiary.addr;

            uint amount = (amountOwed * percentage) / totalBeneficiaryPercentage;

            addr.transfer(amount);
            BeneficiaryPaid(addr, amount);
        }
    }

    struct Beneficiary {
        address addr;
        uint priceShare;
    }

    function pushBeneficiary(address addr, uint priceShare) onlyOwner {
        beneficiaries.push(Beneficiary({
            addr: addr,
            priceShare: priceShare
        }));
    }
}

/*
    Contract to model an assset manager.
*/

contract AssetManager is Mortal {
    mapping(string => address) digitalAssets;
    string[] generatedIds;
    // Map buyer to records of their purchases
    // Optimisation: have a log for each asset
    mapping(address => Record[]) log;
    // Buyers array
    address[] keys;

    function AssetManager() {
        owner = msg.sender;
    }

    event AssetCreated(string generatedId, address assetAddress, string name, string _description, uint _price,
    uint _stock, uint _transferTime, address[] _beneficiaryAddresses, uint[] _priceShare);

    function createDigitalAsset(string generatedId, string name, string description, uint price,
    uint stock, string location, uint transferTime, address[] beneficiaryAddresses, uint[] priceShares){
        require(digitalAssets[name] == address(0x0));
        require(beneficiaryAddresses.length == priceShares.length);

        address assetAddress = new DigitalAsset(generatedId, description, price, stock, transferTime, beneficiaryAddresses, priceShares);
        digitalAssets[generatedId] = assetAddress;
        generatedIds.push(generatedId);
        AssetCreated(generatedId, assetAddress, name, description, price, stock, transferTime, beneficiaryAddresses, priceShares);
    }

    function getAssetPriceByGeneratedId(string generatedId) constant returns (uint) {
        address assetAddress = digitalAssets[generatedId];
        uint price = getAssetPriceByAddr(assetAddress);

        return price;
    }

    function getAssetPriceByAddr(address addr) constant returns (uint) {
        uint price = DigitalAsset(addr).getPrice();

        return price;
    }

    function getAssetAvailableStock(address addr) constant returns (uint) {
        uint availableStock = DigitalAsset(addr).getExistingStock();

        return availableStock;
    }

    // function getAssetGeneratedId(address addr) constant returns (string) {
    //     uint length = generatedIds.length;

    //     for (uint i = 0; i < length; i++) {
    //         if (digitalAssets[generatedIds[i]] == addr){
    //             return generatedIds[i];
    //         }
    //     }
    // }

    event AssetTransfered(address buyer, address asset, uint amount, string recordId);

    // Adding checks to the front-end saves gas that would be unnecessary spent

    function buyAsset(string generatedId, uint amount, string recordId) payable {
        address assetAddress = digitalAssets[generatedId];
        uint price = getAssetPriceByAddr(assetAddress);
        uint availableStock = getAssetAvailableStock(assetAddress);
        uint totalPrice = (price * amount)/2;

        require(availableStock >= amount);
        require (msg.value >= totalPrice);

        DigitalAsset(assetAddress).payBeneficiaries.value(msg.value)(totalPrice);
        DigitalAsset(assetAddress).updateExistingStock(amount);

        setRecord(msg.sender, recordId, assetAddress, AssetStatus.TRANSIT, totalPrice);

        AssetTransfered(msg.sender, assetAddress, amount, recordId);
    }

    event TransactionCompleted(address buyer, address asset, uint amount, string recordId);

    function confirmAsset(string generatedId, uint amount, string recordId) payable {
        address assetAddress = digitalAssets[generatedId];
        uint owed = getAmountOwedFromRecord(msg.sender, recordId);

        require (msg.value >= owed);

        DigitalAsset(assetAddress).payBeneficiaries.value(msg.value)(owed);

        updateStatus(msg.sender, recordId, AssetStatus.CONFIRMED);

        TransactionCompleted(msg.sender, assetAddress, amount, recordId);
    }

    event AddedStock(string name, uint amount);

    function addStock(string name, uint amount) {
        address assetAddress = digitalAssets[name];

        DigitalAsset(assetAddress).addStock(amount);

        AddedStock(name, amount);
    }

    function updateStatus(address buyer, string recordId, AssetStatus status) {
        uint length = keys.length;

        for (uint i = 0; i < length; i++) {
            uint recordsLength = log[keys[i]].length;
            // What if someone buys the same asset more than once
            // Can update to use a generated id instead of asset address
            for (uint j = 0; j < recordsLength; j++){
                if (keccak256(log[keys[i]][j].recordId) == keccak256(recordId)){
                    log[keys[i]][j].status = status;
                    if (status == AssetStatus.CONFIRMED){
                        log[keys[i]][j].owed = 0;
                    }
                }
            }
        }
    }

    function setRecord(address key, string recordId, address assetAddress, AssetStatus status, uint owed) {
        if(log[key].length == 0) {
            keys.push(key);
        }

      log[key].push(Record(recordId, assetAddress, status, owed));
    }

    function getTransferStatus(address buyer, string recordId) constant returns (AssetStatus status) {
        uint length = keys.length;

        for (uint i = 0; i < length; i++) {
            uint recordsLength = log[keys[i]].length;
            // What if someone buys the same asset more than once
            // Can update to use a generated id instead of asset address


            // use less gas by keccak256 instead of loading StringUtils
            for (uint j = 0; j < recordsLength; j++){
                if (keccak256(log[keys[i]][j].recordId) == keccak256(recordId)){
                    status = log[keys[i]][j].status;
                }
            }
        }
    }

    function getAssetAddressFromRecord(address buyer, string recordId) constant returns (address assetAddress) {
        uint length = keys.length;

        for (uint i = 0; i < length; i++) {
            uint recordsLength = log[keys[i]].length;
            // What if someone buys the same asset more than once
            // Can update to use a generated id instead of asset address


            // use less gas by keccak256 instead of loading StringUtils
            for (uint j = 0; j < recordsLength; j++){
                if (keccak256(log[keys[i]][j].recordId) == keccak256(recordId)){
                    assetAddress = log[keys[i]][j].assetAddress;
                }
            }
        }
    }

    function getAmountOwedFromRecord(address buyer, string recordId) constant returns (uint owed) {
        uint length = keys.length;

        for (uint i = 0; i < length; i++) {
            uint recordsLength = log[keys[i]].length;
            // What if someone buys the same asset more than once
            // Can update to use a generated id instead of asset address


            // use less gas by keccak256 instead of loading StringUtils
            for (uint j = 0; j < recordsLength; j++){
                if (keccak256(log[keys[i]][j].recordId) == keccak256(recordId)){
                    owed = log[keys[i]][j].owed;
                }
            }
        }
    }

    struct Record {
        string recordId; // record ID generated by python front-end
        address assetAddress; // address of asset that was bought by the user
        AssetStatus status; // status of asset
        uint owed; // the amount of money to be paid when confirmed
    }

    enum AssetStatus { TRANSIT, DELIVERED, CONFIRMED }
}
