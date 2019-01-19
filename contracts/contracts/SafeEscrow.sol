pragma solidity ^0.5.0;

import "openzeppelin-solidity/contracts/math/SafeMath.sol";
import "openzeppelin-solidity/contracts/ownership/Ownable.sol";

contract SafeEscrow  is Ownable {

    using SafeMath for uint256;

    struct Lender {
        uint deposited_amount;
        uint available_amount;
    }

    struct Profile {
        address lender_address;
        uint    max_risc_score;
        uint    premium_percentage;
    }

    mapping( address => Lender)  lenders;
    Profile[] profiles;

    function() external payable {

    }

    function getLenderInfo(uint index) public view returns(address, uint, uint, uint, uint) {
        Profile storage profile = profiles[index];
        Lender storage lender = lenders[profile.lender_address];
        return (    profile.lender_address,
                    lender.deposited_amount,
                    lender.available_amount,
                    profile.max_risc_score,
                    profile.premium_percentage);
    }



    //function addMeAsLender( uint max_risc_score, uint premium_percentage) public payable {
    //    lender_addresses.push(msg.sender);
    //    lenders[msg.sender] = Lender(msg.value, 0, max_risc_score,premium_percentage);
    //}
}