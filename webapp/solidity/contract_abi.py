abi = """[
	{
		"constant": false,
		"inputs": [
			{
				"name": "name",
				"type": "string"
			},
			{
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "addStock",
		"outputs": [],
		"payable": false,
		"type": "function",
		"stateMutability": "nonpayable"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "generatedId",
				"type": "string"
			},
			{
				"name": "amount",
				"type": "uint256"
			},
			{
				"name": "recordId",
				"type": "string"
			}
		],
		"name": "buyAsset",
		"outputs": [],
		"payable": true,
		"type": "function",
		"stateMutability": "payable"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "generatedId",
				"type": "string"
			},
			{
				"name": "amount",
				"type": "uint256"
			},
			{
				"name": "recordId",
				"type": "string"
			}
		],
		"name": "confirmAsset",
		"outputs": [],
		"payable": true,
		"type": "function",
		"stateMutability": "payable"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "generatedId",
				"type": "string"
			},
			{
				"name": "name",
				"type": "string"
			},
			{
				"name": "description",
				"type": "string"
			},
			{
				"name": "price",
				"type": "uint256"
			},
			{
				"name": "stock",
				"type": "uint256"
			},
			{
				"name": "location",
				"type": "string"
			},
			{
				"name": "transferTime",
				"type": "uint256"
			},
			{
				"name": "beneficiaryAddresses",
				"type": "address[]"
			},
			{
				"name": "priceShares",
				"type": "uint256[]"
			}
		],
		"name": "createDigitalAsset",
		"outputs": [],
		"payable": false,
		"type": "function",
		"stateMutability": "nonpayable"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "remove",
		"outputs": [],
		"payable": false,
		"type": "function",
		"stateMutability": "nonpayable"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "key",
				"type": "address"
			},
			{
				"name": "recordId",
				"type": "string"
			},
			{
				"name": "assetAddress",
				"type": "address"
			},
			{
				"name": "status",
				"type": "uint8"
			},
			{
				"name": "owed",
				"type": "uint256"
			}
		],
		"name": "setRecord",
		"outputs": [],
		"payable": false,
		"type": "function",
		"stateMutability": "nonpayable"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "buyer",
				"type": "address"
			},
			{
				"name": "recordId",
				"type": "string"
			},
			{
				"name": "status",
				"type": "uint8"
			}
		],
		"name": "updateStatus",
		"outputs": [],
		"payable": false,
		"type": "function",
		"stateMutability": "nonpayable"
	},
	{
		"inputs": [],
		"payable": false,
		"type": "constructor",
		"stateMutability": "nonpayable"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"name": "generatedId",
				"type": "string"
			},
			{
				"indexed": false,
				"name": "assetAddress",
				"type": "address"
			},
			{
				"indexed": false,
				"name": "name",
				"type": "string"
			},
			{
				"indexed": false,
				"name": "_description",
				"type": "string"
			},
			{
				"indexed": false,
				"name": "_price",
				"type": "uint256"
			},
			{
				"indexed": false,
				"name": "_stock",
				"type": "uint256"
			},
			{
				"indexed": false,
				"name": "_transferTime",
				"type": "uint256"
			},
			{
				"indexed": false,
				"name": "_beneficiaryAddresses",
				"type": "address[]"
			},
			{
				"indexed": false,
				"name": "_priceShare",
				"type": "uint256[]"
			}
		],
		"name": "AssetCreated",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"name": "buyer",
				"type": "address"
			},
			{
				"indexed": false,
				"name": "asset",
				"type": "address"
			},
			{
				"indexed": false,
				"name": "amount",
				"type": "uint256"
			},
			{
				"indexed": false,
				"name": "recordId",
				"type": "string"
			}
		],
		"name": "AssetTransfered",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"name": "buyer",
				"type": "address"
			},
			{
				"indexed": false,
				"name": "asset",
				"type": "address"
			},
			{
				"indexed": false,
				"name": "amount",
				"type": "uint256"
			},
			{
				"indexed": false,
				"name": "recordId",
				"type": "string"
			}
		],
		"name": "TransactionCompleted",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"name": "name",
				"type": "string"
			},
			{
				"indexed": false,
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "AddedStock",
		"type": "event"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "buyer",
				"type": "address"
			},
			{
				"name": "recordId",
				"type": "string"
			}
		],
		"name": "getAmountOwedFromRecord",
		"outputs": [
			{
				"name": "owed",
				"type": "uint256"
			}
		],
		"payable": false,
		"type": "function",
		"stateMutability": "view"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "buyer",
				"type": "address"
			},
			{
				"name": "recordId",
				"type": "string"
			}
		],
		"name": "getAssetAddressFromRecord",
		"outputs": [
			{
				"name": "assetAddress",
				"type": "address"
			}
		],
		"payable": false,
		"type": "function",
		"stateMutability": "view"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "addr",
				"type": "address"
			}
		],
		"name": "getAssetAvailableStock",
		"outputs": [
			{
				"name": "",
				"type": "uint256"
			}
		],
		"payable": false,
		"type": "function",
		"stateMutability": "view"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "addr",
				"type": "address"
			}
		],
		"name": "getAssetPriceByAddr",
		"outputs": [
			{
				"name": "",
				"type": "uint256"
			}
		],
		"payable": false,
		"type": "function",
		"stateMutability": "view"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "generatedId",
				"type": "string"
			}
		],
		"name": "getAssetPriceByGeneratedId",
		"outputs": [
			{
				"name": "",
				"type": "uint256"
			}
		],
		"payable": false,
		"type": "function",
		"stateMutability": "view"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "buyer",
				"type": "address"
			},
			{
				"name": "recordId",
				"type": "string"
			}
		],
		"name": "getTransferStatus",
		"outputs": [
			{
				"name": "status",
				"type": "uint8"
			}
		],
		"payable": false,
		"type": "function",
		"stateMutability": "view"
	}
]"""