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

def get_lenders():
	w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/41d6ff4c88864dd996974369a8f27c81"))
	escrow_address='0x56A3138c0Cb79674EC56E4fc2217033c1f438845'
	contract = w3.eth.contract(address=escrow_address, abi=ABI)

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

	lender_profile = {}
	for lender in lenders:
		max_lender_risk_score = lender.get('max_risc_score')
		max_premium_for_risk = lender_profile.get(max_lender_risk_score, 100)

		if max_premium_for_risk > lender['premium_percentage']:
			max_premium_for_risk = lender['premium_percentage']
		lender_profile[max_lender_risk_score] = max_premium_for_risk
	lender_profile_sorted = [(key, value) for key, value in lender_profile.items()]
	lender_profile_sorted.sort(key=lambda x: x[0])

	continous_profile = []
	prev_lender_risk = 0

	for lender_risk, lender_premium in lender_profile_sorted:
		continous_profile.extend([(str(i+1), lender_premium) for i in range(prev_lender_risk, lender_risk)])
		prev_lender_risk = lender_risk
	return continous_profile
