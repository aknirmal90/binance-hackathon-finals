pragma solidity 0.4.25;

import "openzeppelin-solidity/contracts/math/SafeMath.sol";
import "openzeppelin-solidity/contracts/ownership/Ownable.sol";

import "github.com/oraclize/ethereum-api/oraclizeAPI_0.4.sol";


contract SafeEscrow  is Ownable, usingOraclize {

    using SafeMath for uint256;

    struct Lender {
        uint deposited_amount;
        uint locked_amount;
    }

    struct Profile {
        address lender_address;
        uint    max_risk_score;
        uint    premium_percentage;
    }

    struct Insurance {

        address sender;
        address destination;

        uint    amount;

        uint    risk_score;
        uint    profile_index;

        uint    premium_fee;

    }

    mapping( address => Lender)  lenders;

    Profile[]       profiles;
    Insurance[]     insurances;

    mapping ( bytes32 => Insurance) quotes;

    event Deposit(address indexed lender, uint amount, uint total_deposited_amount);
    event Withdraw(address indexed lender, uint amount, uint total_deposited_amount);
    event NewProfile(address indexed lender, uint max_risk_score, uint premium_percentage);
    event NewQuote(address indexed sender, address indexed receiver, uint amount);
    event DoneQuote(address indexed sender, address indexed receiver, uint amount, uint risk_score);


    // lender deposit amount using fallback payable
    function() external payable {
        lenders[msg.sender].deposited_amount = lenders[msg.sender].deposited_amount.add(msg.value);

        emit Deposit(msg.sender, msg.value, lenders[msg.sender].deposited_amount);
    }

    // specify the condition of the lending
    function addProfile( uint max_risk_score, uint premium_percentage) external {
        require(lenders[msg.sender].deposited_amount>0);

        profiles.push(Profile(msg.sender,max_risk_score,premium_percentage));

        emit NewProfile(msg.sender, max_risk_score, premium_percentage);

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
                    profile.max_risk_score,
                    profile.premium_percentage);
    }

    function insureTransfer( address destination ) external payable {

        string memory scoring_system_url = string(abi.encodePacked(
                "json(https://hackathon-229016.appspot.com/api/?destination_address=0x",
                toAsciiString(address(destination)), ").score"));

        bytes32 query_id = oraclize_query("URL", scoring_system_url);

        quotes[query_id] = Insurance(msg.sender, destination, msg.value, 0, 0, 0);

        emit NewQuote( msg.sender, destination, msg.value);
    }

    function __callback(bytes32 myid, string result) public {
       if (msg.sender != oraclize_cbAddress()) revert();

       Insurance storage insurance = quotes[myid];
       require(insurance.sender!=address(0));

       uint risk_score = parseInt(result);

       // TODO: find appropriate lender
       // TODO: calculate premium
       // TODO: send funds

       emit DoneQuote(insurance.sender, insurance.destination, insurance.amount, risk_score);
    }

    // TODO: dispute resolution

    function toAsciiString(address x) pure private returns (string memory) {
        bytes memory s = new bytes(40);
        for (uint i = 0; i < 20; i++) {
            byte b = byte(uint8(uint(x) / (2**(8*(19 - i)))));
            byte hi = byte(uint8(b) / 16);
            byte lo = byte(uint8(b) - 16 * uint8(hi));
            s[2*i] = char(hi);
            s[2*i+1] = char(lo);
        }
        return string(s);
    }

    function char(byte b) pure private returns (byte c) {
        if (b < 10) return byte(uint8(b) + 0x30);
        else return byte(uint8(b) + 0x57);
    }


}