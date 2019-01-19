from web3 import Web3
import json

abi = '''[
	{
		"constant": true,
		"inputs": [
			{
				"name": "index",
				"type": "uint256"
			}
		],
		"name": "getLenderInfo",
		"outputs": [
			{
				"name": "",
				"type": "address"
			},
			{
				"name": "",
				"type": "uint256"
			},
			{
				"name": "",
				"type": "uint256"
			},
			{
				"name": "",
				"type": "uint256"
			},
			{
				"name": "",
				"type": "uint256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	}
]'''

ABI = json.loads(abi)

def lenders():
    w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/41d6ff4c88864dd996974369a8f27c81"))
    contract = w3.eth.contract(address='0x56A3138c0Cb79674EC56E4fc2217033c1f438845', abi=ABI)
    i = 0
    lenders = []
    while i < 10:
        try:
            lender_info = contract.functions.getLenderInfo(i).call()
            lenders.append({
                'address': lender_info[0],
                'deposited_amount': lender_info[1],
                'available_amount': lender_info[2],
                'max_risc_score': lender_info[3],
                'premium_percentage': lender_info[4]
            })
        except:
            break
        i+=1
    return lenders