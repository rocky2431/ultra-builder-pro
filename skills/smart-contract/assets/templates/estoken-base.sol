// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/// @title esToken - Escrowed Token with Vesting
/// @author [Your Name]
/// @notice Non-transferable escrowed token that vests linearly to underlying token
/// @dev Users stake underlying token to receive esToken, then vest esToken back to underlying
contract EsToken is ERC20, Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    /*//////////////////////////////////////////////////////////////
                                CONSTANTS
    //////////////////////////////////////////////////////////////*/

    uint256 public constant VESTING_DURATION = 365 days;
    uint256 public constant MINIMUM_VEST_AMOUNT = 1e18;

    /*//////////////////////////////////////////////////////////////
                            STATE VARIABLES
    //////////////////////////////////////////////////////////////*/

    IERC20 public immutable underlyingToken;

    struct VestingPosition {
        uint256 amount;         // Total esToken amount being vested
        uint256 startTime;      // Vesting start timestamp
        uint256 claimed;        // Amount of underlying already claimed
    }

    mapping(address => VestingPosition[]) public vestingPositions;
    mapping(address => bool) public transferWhitelist;

    uint256 public totalVesting;  // Total esToken currently in vesting

    /*//////////////////////////////////////////////////////////////
                                 ERRORS
    //////////////////////////////////////////////////////////////*/

    error TransferNotAllowed();
    error InvalidAmount();
    error NoClaimableTokens();
    error VestingPositionNotFound();
    error InsufficientBalance();

    /*//////////////////////////////////////////////////////////////
                                 EVENTS
    //////////////////////////////////////////////////////////////*/

    event Staked(address indexed user, uint256 amount);
    event VestingStarted(address indexed user, uint256 indexed positionId, uint256 amount);
    event Claimed(address indexed user, uint256 indexed positionId, uint256 amount);
    event VestingCancelled(address indexed user, uint256 indexed positionId, uint256 remaining);

    /*//////////////////////////////////////////////////////////////
                              CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/

    /// @notice Initialize esToken with underlying token
    /// @param underlyingToken_ Address of the underlying token
    /// @param name_ Token name (e.g., "Escrowed TOKEN")
    /// @param symbol_ Token symbol (e.g., "esTOKEN")
    constructor(
        address underlyingToken_,
        string memory name_,
        string memory symbol_
    ) ERC20(name_, symbol_) Ownable(msg.sender) {
        underlyingToken = IERC20(underlyingToken_);
    }

    /*//////////////////////////////////////////////////////////////
                            STAKING FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Stake underlying tokens to receive esTokens 1:1
    /// @param amount Amount of underlying tokens to stake
    function stake(uint256 amount) external nonReentrant {
        if (amount == 0) revert InvalidAmount();

        underlyingToken.safeTransferFrom(msg.sender, address(this), amount);
        _mint(msg.sender, amount);

        emit Staked(msg.sender, amount);
    }

    /*//////////////////////////////////////////////////////////////
                            VESTING FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Start vesting esTokens to receive underlying tokens linearly
    /// @param amount Amount of esTokens to vest
    /// @return positionId The ID of the created vesting position
    function startVesting(uint256 amount) external nonReentrant returns (uint256 positionId) {
        if (amount < MINIMUM_VEST_AMOUNT) revert InvalidAmount();
        if (balanceOf(msg.sender) < amount) revert InsufficientBalance();

        // Burn esTokens from user
        _burn(msg.sender, amount);

        // Create vesting position
        vestingPositions[msg.sender].push(VestingPosition({
            amount: amount,
            startTime: block.timestamp,
            claimed: 0
        }));

        positionId = vestingPositions[msg.sender].length - 1;
        totalVesting += amount;

        emit VestingStarted(msg.sender, positionId, amount);
    }

    /// @notice Claim vested underlying tokens from a specific position
    /// @param positionId ID of the vesting position
    function claim(uint256 positionId) external nonReentrant {
        VestingPosition storage position = _getPosition(msg.sender, positionId);

        uint256 claimable = _calculateClaimable(position);
        if (claimable == 0) revert NoClaimableTokens();

        position.claimed += claimable;
        totalVesting -= claimable;

        underlyingToken.safeTransfer(msg.sender, claimable);

        emit Claimed(msg.sender, positionId, claimable);
    }

    /// @notice Claim all vested tokens from all positions
    function claimAll() external nonReentrant {
        VestingPosition[] storage positions = vestingPositions[msg.sender];
        uint256 totalClaimable;

        for (uint256 i = 0; i < positions.length;) {
            uint256 claimable = _calculateClaimable(positions[i]);
            if (claimable > 0) {
                positions[i].claimed += claimable;
                totalClaimable += claimable;
                emit Claimed(msg.sender, i, claimable);
            }
            unchecked { i++; }
        }

        if (totalClaimable == 0) revert NoClaimableTokens();

        totalVesting -= totalClaimable;
        underlyingToken.safeTransfer(msg.sender, totalClaimable);
    }

    /// @notice Cancel vesting and return remaining esTokens (forfeits unvested portion)
    /// @param positionId ID of the vesting position to cancel
    function cancelVesting(uint256 positionId) external nonReentrant {
        VestingPosition storage position = _getPosition(msg.sender, positionId);

        // Calculate what can be claimed
        uint256 claimable = _calculateClaimable(position);
        uint256 remaining = position.amount - position.claimed - claimable;

        // Mark position as fully claimed
        position.claimed = position.amount;
        totalVesting -= (claimable + remaining);

        // Transfer claimable underlying
        if (claimable > 0) {
            underlyingToken.safeTransfer(msg.sender, claimable);
        }

        // Return remaining as esTokens
        if (remaining > 0) {
            _mint(msg.sender, remaining);
        }

        emit VestingCancelled(msg.sender, positionId, remaining);
    }

    /*//////////////////////////////////////////////////////////////
                            VIEW FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Get claimable amount for a specific position
    /// @param user Address of the user
    /// @param positionId ID of the vesting position
    /// @return claimable Amount of underlying tokens claimable
    function getClaimable(address user, uint256 positionId) external view returns (uint256 claimable) {
        if (positionId >= vestingPositions[user].length) return 0;
        return _calculateClaimable(vestingPositions[user][positionId]);
    }

    /// @notice Get total claimable across all positions
    /// @param user Address of the user
    /// @return totalClaimable Total claimable underlying tokens
    function getTotalClaimable(address user) external view returns (uint256 totalClaimable) {
        VestingPosition[] storage positions = vestingPositions[user];
        for (uint256 i = 0; i < positions.length;) {
            totalClaimable += _calculateClaimable(positions[i]);
            unchecked { i++; }
        }
    }

    /// @notice Get number of vesting positions for a user
    /// @param user Address of the user
    /// @return count Number of vesting positions
    function getVestingPositionCount(address user) external view returns (uint256 count) {
        return vestingPositions[user].length;
    }

    /// @notice Get vesting progress for a position
    /// @param user Address of the user
    /// @param positionId ID of the vesting position
    /// @return vested Amount already vested
    /// @return total Total amount in position
    /// @return percentComplete Percentage complete (basis points, 10000 = 100%)
    function getVestingProgress(
        address user,
        uint256 positionId
    ) external view returns (uint256 vested, uint256 total, uint256 percentComplete) {
        if (positionId >= vestingPositions[user].length) {
            return (0, 0, 0);
        }

        VestingPosition storage position = vestingPositions[user][positionId];
        total = position.amount;
        vested = _calculateVested(position);
        percentComplete = total > 0 ? (vested * 10000) / total : 0;
    }

    /*//////////////////////////////////////////////////////////////
                            ADMIN FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Add address to transfer whitelist (for staking contracts, etc.)
    /// @param account Address to whitelist
    /// @param allowed Whether to allow transfers
    function setTransferWhitelist(address account, bool allowed) external onlyOwner {
        transferWhitelist[account] = allowed;
    }

    /*//////////////////////////////////////////////////////////////
                          INTERNAL FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    function _getPosition(
        address user,
        uint256 positionId
    ) internal view returns (VestingPosition storage) {
        if (positionId >= vestingPositions[user].length) {
            revert VestingPositionNotFound();
        }
        return vestingPositions[user][positionId];
    }

    function _calculateVested(VestingPosition storage position) internal view returns (uint256) {
        uint256 elapsed = block.timestamp - position.startTime;
        if (elapsed >= VESTING_DURATION) {
            return position.amount;
        }
        return (position.amount * elapsed) / VESTING_DURATION;
    }

    function _calculateClaimable(VestingPosition storage position) internal view returns (uint256) {
        uint256 vested = _calculateVested(position);
        return vested > position.claimed ? vested - position.claimed : 0;
    }

    /*//////////////////////////////////////////////////////////////
                          TRANSFER RESTRICTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Override transfer to restrict to whitelisted addresses only
    function transfer(address to, uint256 amount) public override returns (bool) {
        if (!transferWhitelist[msg.sender] && !transferWhitelist[to]) {
            revert TransferNotAllowed();
        }
        return super.transfer(to, amount);
    }

    /// @notice Override transferFrom to restrict to whitelisted addresses only
    function transferFrom(address from, address to, uint256 amount) public override returns (bool) {
        if (!transferWhitelist[from] && !transferWhitelist[to]) {
            revert TransferNotAllowed();
        }
        return super.transferFrom(from, to, amount);
    }
}
