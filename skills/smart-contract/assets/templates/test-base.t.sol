// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {Test, console2} from "forge-std/Test.sol";
// Import your contract here:
// import {MyContract} from "../src/MyContract.sol";

/// @title Contract Test Suite
/// @notice Comprehensive tests including unit, fuzz, and invariant tests
contract ContractTest is Test {
    /*//////////////////////////////////////////////////////////////
                            STATE VARIABLES
    //////////////////////////////////////////////////////////////*/

    // Contract under test
    // MyContract public myContract;

    // Test actors
    address public owner;
    address public user1;
    address public user2;
    address public attacker;

    // Test constants
    uint256 public constant INITIAL_BALANCE = 1000 ether;

    /*//////////////////////////////////////////////////////////////
                                 EVENTS
    //////////////////////////////////////////////////////////////*/

    // Copy events from contract for testing
    // event Transfer(address indexed from, address indexed to, uint256 value);

    /*//////////////////////////////////////////////////////////////
                                 SETUP
    //////////////////////////////////////////////////////////////*/

    function setUp() public {
        // Create labeled addresses
        owner = makeAddr("owner");
        user1 = makeAddr("user1");
        user2 = makeAddr("user2");
        attacker = makeAddr("attacker");

        // Fund accounts
        vm.deal(owner, INITIAL_BALANCE);
        vm.deal(user1, INITIAL_BALANCE);
        vm.deal(user2, INITIAL_BALANCE);

        // Deploy contract
        vm.startPrank(owner);
        // myContract = new MyContract(...);
        vm.stopPrank();
    }

    /*//////////////////////////////////////////////////////////////
                            DEPLOYMENT TESTS
    //////////////////////////////////////////////////////////////*/

    function test_Deployment_InitialState() public view {
        // assertEq(myContract.owner(), owner);
        // assertEq(myContract.totalSupply(), 0);
    }

    function test_Deployment_RevertsWithInvalidParams() public {
        // vm.expectRevert(MyContract.InvalidParameter.selector);
        // new MyContract(address(0));
    }

    /*//////////////////////////////////////////////////////////////
                            UNIT TESTS
    //////////////////////////////////////////////////////////////*/

    /// @notice Test successful function execution
    function test_FunctionName_Success() public {
        // Arrange
        // vm.prank(user1);

        // Act
        // myContract.someFunction(params);

        // Assert
        // assertEq(myContract.value(), expectedValue);
    }

    /// @notice Test function reverts with invalid input
    function test_FunctionName_RevertsWithInvalidInput() public {
        vm.prank(user1);

        // vm.expectRevert(MyContract.InvalidInput.selector);
        // myContract.someFunction(invalidParams);
    }

    /// @notice Test access control
    function test_AdminFunction_RevertsWhenCalledByNonOwner() public {
        vm.prank(user1);

        // vm.expectRevert("Ownable: caller is not the owner");
        // myContract.adminFunction();
    }

    /// @notice Test event emission
    function test_Function_EmitsEvent() public {
        // vm.expectEmit(true, true, false, true);
        // emit Transfer(user1, user2, 100);

        // vm.prank(user1);
        // myContract.transfer(user2, 100);
    }

    /*//////////////////////////////////////////////////////////////
                              FUZZ TESTS
    //////////////////////////////////////////////////////////////*/

    /// @notice Fuzz test with bounded inputs
    function testFuzz_Function_WithValidRange(uint256 amount) public {
        // Bound input to valid range
        amount = bound(amount, 1, INITIAL_BALANCE);

        // vm.prank(user1);
        // myContract.deposit{value: amount}();

        // assertEq(myContract.balanceOf(user1), amount);
    }

    /// @notice Fuzz test with multiple parameters
    function testFuzz_Transfer_AnyValidAmount(
        uint256 amount,
        address recipient
    ) public {
        // Exclude invalid addresses
        vm.assume(recipient != address(0));
        // vm.assume(recipient != address(myContract));
        vm.assume(recipient.code.length == 0); // EOA only

        // Bound amount
        amount = bound(amount, 1, INITIAL_BALANCE);

        // Test logic here
    }

    /*//////////////////////////////////////////////////////////////
                            EDGE CASE TESTS
    //////////////////////////////////////////////////////////////*/

    function test_EdgeCase_ZeroAmount() public {
        vm.prank(user1);

        // vm.expectRevert(MyContract.InvalidAmount.selector);
        // myContract.deposit{value: 0}();
    }

    function test_EdgeCase_MaxAmount() public {
        // Test with type(uint256).max or other boundaries
    }

    function test_EdgeCase_EmptyArray() public {
        // address[] memory empty = new address[](0);
        // vm.expectRevert(MyContract.EmptyArray.selector);
        // myContract.batchProcess(empty);
    }

    /*//////////////////////////////////////////////////////////////
                          REENTRANCY TESTS
    //////////////////////////////////////////////////////////////*/

    function test_Reentrancy_WithdrawProtected() public {
        // Deploy attacker contract
        // ReentrancyAttacker attackerContract = new ReentrancyAttacker(address(myContract));

        // Fund attacker
        // vm.deal(address(attackerContract), 1 ether);

        // Attack should fail
        // vm.expectRevert();
        // attackerContract.attack();
    }

    /*//////////////////////////////////////////////////////////////
                          TIME-BASED TESTS
    //////////////////////////////////////////////////////////////*/

    function test_TimeLock_RevertsBeforeDeadline() public {
        // vm.expectRevert(MyContract.TooEarly.selector);
        // myContract.timedFunction();

        // Fast forward
        skip(1 days);

        // Should work now
        // myContract.timedFunction();
    }

    function test_Expiry_RevertsAfterDeadline() public {
        // Fast forward past deadline
        skip(30 days);

        // vm.expectRevert(MyContract.Expired.selector);
        // myContract.timedFunction();
    }

    /*//////////////////////////////////////////////////////////////
                            GAS BENCHMARKS
    //////////////////////////////////////////////////////////////*/

    function test_Gas_Function() public {
        uint256 gasBefore = gasleft();

        // vm.prank(user1);
        // myContract.someFunction();

        uint256 gasUsed = gasBefore - gasleft();
        console2.log("Gas used:", gasUsed);

        // Assert gas is within expected range
        assertLt(gasUsed, 100_000);
    }

    /*//////////////////////////////////////////////////////////////
                            HELPER FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    function _setupUserWithBalance(address user, uint256 amount) internal {
        vm.deal(user, amount);
        // vm.prank(user);
        // myContract.deposit{value: amount}();
    }
}

/*//////////////////////////////////////////////////////////////
                          INVARIANT TESTS
//////////////////////////////////////////////////////////////*/

/// @title Invariant Test Suite
/// @notice Tests that protocol invariants always hold
contract ContractInvariantTest is Test {
    // MyContract public myContract;
    // ContractHandler public handler;

    function setUp() public {
        // Deploy contract
        // myContract = new MyContract();

        // Deploy handler
        // handler = new ContractHandler(myContract);

        // Target only the handler
        // targetContract(address(handler));
    }

    /// @notice Total supply should always equal sum of all balances
    function invariant_BalancesSumToTotalSupply() public view {
        // uint256 sum = myContract.balanceOf(address1) + myContract.balanceOf(address2);
        // assertEq(myContract.totalSupply(), sum);
    }

    /// @notice Contract ETH balance should match deposits minus withdrawals
    function invariant_ContractBalanceConsistent() public view {
        // assertEq(address(myContract).balance, handler.totalDeposited() - handler.totalWithdrawn());
    }
}

/*//////////////////////////////////////////////////////////////
                          ATTACK CONTRACTS
//////////////////////////////////////////////////////////////*/

/// @notice Reentrancy attacker for testing
contract ReentrancyAttacker {
    // address public target;
    // uint256 public attackCount;

    // constructor(address _target) {
    //     target = _target;
    // }

    // function attack() external payable {
    //     ITarget(target).deposit{value: msg.value}();
    //     ITarget(target).withdraw(msg.value);
    // }

    // receive() external payable {
    //     if (attackCount < 5 && target.balance >= 1 ether) {
    //         attackCount++;
    //         ITarget(target).withdraw(1 ether);
    //     }
    // }
}

/*//////////////////////////////////////////////////////////////
                            HANDLER
//////////////////////////////////////////////////////////////*/

/// @notice Handler for invariant testing
contract ContractHandler is Test {
    // MyContract public target;
    // address[] public actors;
    // uint256 public totalDeposited;
    // uint256 public totalWithdrawn;

    // constructor(MyContract _target) {
    //     target = _target;
    //     actors.push(makeAddr("actor1"));
    //     actors.push(makeAddr("actor2"));
    //     actors.push(makeAddr("actor3"));
    // }

    // function deposit(uint256 actorSeed, uint256 amount) public {
    //     address actor = actors[actorSeed % actors.length];
    //     amount = bound(amount, 0.01 ether, 10 ether);

    //     vm.deal(actor, amount);
    //     vm.prank(actor);
    //     target.deposit{value: amount}();

    //     totalDeposited += amount;
    // }

    // function withdraw(uint256 actorSeed, uint256 amount) public {
    //     address actor = actors[actorSeed % actors.length];
    //     uint256 balance = target.balanceOf(actor);
    //     amount = bound(amount, 0, balance);

    //     if (amount > 0) {
    //         vm.prank(actor);
    //         target.withdraw(amount);
    //         totalWithdrawn += amount;
    //     }
    // }
}
