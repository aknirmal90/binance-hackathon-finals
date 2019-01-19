pragma solidity ^0.5.0;

import "openzeppelin-solidity/contracts/math/SafeMath.sol";
import "openzeppelin-solidity/contracts/ownership/Ownable.sol";

contract SafeEscrow  is Ownable {

    using SafeMath for uint256;

    struct Lender {
        uint deposited_amount;
        uint locked_amount;
    }

    struct Profile {
        address lender_address;
        uint    max_risc_score;
        uint    premium_percentage;
    }

    mapping( address => Lender)  lenders;
    Profile[] profiles;


    event Deposit(address indexed lender, uint amount, uint total_deposited_amount);
    event Withdraw(address indexed lender, uint amount, uint total_deposited_amount);
    event NewProfile(address indexed lender, uint max_risc_score, uint premium_percentage);


    // lender deposit amount using fallback payable
    function() external payable {
        lenders[msg.sender].deposited_amount = lenders[msg.sender].deposited_amount.add(msg.value);

        emit Deposit(msg.sender, msg.value, lenders[msg.sender].deposited_amount);
    }

    // specify the condition of the lending
    function addProfile( uint max_risc_score, uint premium_percentage) external {
        require(lenders[msg.sender].deposited_amount>0);

        profiles.push(Profile(msg.sender,max_risc_score,premium_percentage));

        emit NewProfile(msg.sender, max_risc_score, premium_percentage);

    }

    // lender can withdraw funds, not including locked amount
    function withdraw(uint amount) external {
        Lender storage lender = lenders[msg.sender];

        require(lender.deposited_amount>=lender.locked_amount.add(amount));
        require(amount>0);

        lender.deposited_amount = lender.deposited_amount.sub(amount);

        msg.sender.transfer(amount);

        emit Withdraw(msg.sender, amount, lenders[msg.sender].deposited_amount);
    }

    /// get lender information
    function getLenderInfo(uint index) public view returns(address, uint, uint, uint, uint) {
        Profile storage profile = profiles[index];
        Lender storage lender = lenders[profile.lender_address];
        return (    profile.lender_address,
                    lender.deposited_amount,
                    lender.deposited_amount.sub(lender.locked_amount),
                    profile.max_risc_score,
                    profile.premium_percentage);
    }

}