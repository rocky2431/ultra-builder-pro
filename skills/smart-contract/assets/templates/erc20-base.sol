// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {ERC20Burnable} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import {ERC20Permit} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/// @title ERC20 Base Token
/// @author [Your Name]
/// @notice Standard ERC20 token with mint, burn, and permit functionality
/// @dev Includes common extensions for production use
contract ERC20Base is ERC20, ERC20Burnable, ERC20Permit, Ownable, ReentrancyGuard {
    /*//////////////////////////////////////////////////////////////
                                CONSTANTS
    //////////////////////////////////////////////////////////////*/

    uint256 public constant MAX_SUPPLY = 1_000_000_000e18; // 1 billion tokens

    /*//////////////////////////////////////////////////////////////
                                 ERRORS
    //////////////////////////////////////////////////////////////*/

    error ExceedsMaxSupply(uint256 requested, uint256 available);
    error InvalidRecipient();
    error InvalidAmount();

    /*//////////////////////////////////////////////////////////////
                                 EVENTS
    //////////////////////////////////////////////////////////////*/

    event TokensMinted(address indexed to, uint256 amount);

    /*//////////////////////////////////////////////////////////////
                              CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/

    /// @notice Initializes the token with name, symbol, and initial supply
    /// @param name_ Token name
    /// @param symbol_ Token symbol
    /// @param initialSupply_ Initial supply to mint to deployer
    constructor(
        string memory name_,
        string memory symbol_,
        uint256 initialSupply_
    ) ERC20(name_, symbol_) ERC20Permit(name_) Ownable(msg.sender) {
        if (initialSupply_ > MAX_SUPPLY) {
            revert ExceedsMaxSupply(initialSupply_, MAX_SUPPLY);
        }
        _mint(msg.sender, initialSupply_);
    }

    /*//////////////////////////////////////////////////////////////
                            EXTERNAL FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Mints new tokens to specified address
    /// @dev Only callable by owner, respects MAX_SUPPLY
    /// @param to Recipient address
    /// @param amount Amount to mint
    function mint(address to, uint256 amount) external onlyOwner {
        if (to == address(0)) revert InvalidRecipient();
        if (amount == 0) revert InvalidAmount();

        uint256 newSupply = totalSupply() + amount;
        if (newSupply > MAX_SUPPLY) {
            revert ExceedsMaxSupply(newSupply, MAX_SUPPLY - totalSupply());
        }

        _mint(to, amount);
        emit TokensMinted(to, amount);
    }

    /*//////////////////////////////////////////////////////////////
                            VIEW FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Returns remaining mintable supply
    /// @return Amount of tokens that can still be minted
    function remainingMintableSupply() external view returns (uint256) {
        return MAX_SUPPLY - totalSupply();
    }
}
