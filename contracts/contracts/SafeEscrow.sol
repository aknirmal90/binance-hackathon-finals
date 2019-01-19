pragma solidity ^0.4.25;

contract SafeEscrow  {

    struct Lender {
        uint deposited_amount;
        uint available_amount;
        uint max_risc_score;
        uint premium_percentage;
    }

    address[] public lender_addresses;
    mapping( address => Lender)  lenders;

    function getLenderInfo(uint index) public view returns(address, uint, uint, uint, uint) {
        address lender_address = lender_addresses[index];
        Lender storage lender = lenders[lender_address];
        return (    lender_address,
                    lender.deposited_amount,
                    lender.available_amount,
                    lender.max_risc_score,
                    lender.premium_percentage);
    }

    function addMeAsLender( uint max_risc_score, uint premium_percentage) public payable {
        lender_addresses.push(msg.sender);
        lenders[msg.sender] = Lender(msg.value, 0, max_risc_score,premium_percentage);
    }

}