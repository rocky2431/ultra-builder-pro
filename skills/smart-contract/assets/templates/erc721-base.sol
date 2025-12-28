// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;

import {ERC721} from "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import {ERC721Enumerable} from "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import {ERC721URIStorage} from "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import {Strings} from "@openzeppelin/contracts/utils/Strings.sol";
import {MerkleProof} from "@openzeppelin/contracts/utils/cryptography/MerkleProof.sol";

/// @title ERC721 Base NFT
/// @author [Your Name]
/// @notice NFT collection with whitelist, public mint, and reveal functionality
/// @dev Includes enumerable, URI storage, and merkle proof whitelist
contract ERC721Base is ERC721, ERC721Enumerable, ERC721URIStorage, Ownable, ReentrancyGuard {
    using Strings for uint256;

    /*//////////////////////////////////////////////////////////////
                                CONSTANTS
    //////////////////////////////////////////////////////////////*/

    uint256 public constant MAX_SUPPLY = 10_000;
    uint256 public constant MAX_PER_WALLET = 5;
    uint256 public constant WHITELIST_PRICE = 0.05 ether;
    uint256 public constant PUBLIC_PRICE = 0.08 ether;

    /*//////////////////////////////////////////////////////////////
                            STATE VARIABLES
    //////////////////////////////////////////////////////////////*/

    uint256 private _tokenIdCounter;
    string private _baseTokenURI;
    string private _hiddenMetadataURI;
    bytes32 public merkleRoot;

    bool public revealed;
    bool public whitelistMintEnabled;
    bool public publicMintEnabled;

    mapping(address => uint256) public mintedCount;

    /*//////////////////////////////////////////////////////////////
                                 ERRORS
    //////////////////////////////////////////////////////////////*/

    error MintNotEnabled();
    error ExceedsMaxSupply();
    error ExceedsMaxPerWallet();
    error InsufficientPayment(uint256 required, uint256 sent);
    error InvalidProof();
    error WithdrawalFailed();

    /*//////////////////////////////////////////////////////////////
                                 EVENTS
    //////////////////////////////////////////////////////////////*/

    event WhitelistMint(address indexed to, uint256 quantity);
    event PublicMint(address indexed to, uint256 quantity);
    event Revealed(string baseURI);

    /*//////////////////////////////////////////////////////////////
                              CONSTRUCTOR
    //////////////////////////////////////////////////////////////*/

    constructor(
        string memory name_,
        string memory symbol_,
        string memory hiddenMetadataURI_
    ) ERC721(name_, symbol_) Ownable(msg.sender) {
        _hiddenMetadataURI = hiddenMetadataURI_;
    }

    /*//////////////////////////////////////////////////////////////
                            MINT FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @notice Whitelist mint with merkle proof verification
    /// @param quantity Number of tokens to mint
    /// @param merkleProof Proof for whitelist verification
    function whitelistMint(
        uint256 quantity,
        bytes32[] calldata merkleProof
    ) external payable nonReentrant {
        if (!whitelistMintEnabled) revert MintNotEnabled();
        if (_tokenIdCounter + quantity > MAX_SUPPLY) revert ExceedsMaxSupply();
        if (mintedCount[msg.sender] + quantity > MAX_PER_WALLET) revert ExceedsMaxPerWallet();

        uint256 cost = WHITELIST_PRICE * quantity;
        if (msg.value < cost) revert InsufficientPayment(cost, msg.value);

        bytes32 leaf = keccak256(abi.encodePacked(msg.sender));
        if (!MerkleProof.verify(merkleProof, merkleRoot, leaf)) revert InvalidProof();

        mintedCount[msg.sender] += quantity;

        for (uint256 i = 0; i < quantity;) {
            _safeMint(msg.sender, _tokenIdCounter);
            unchecked {
                _tokenIdCounter++;
                i++;
            }
        }

        emit WhitelistMint(msg.sender, quantity);
    }

    /// @notice Public mint
    /// @param quantity Number of tokens to mint
    function publicMint(uint256 quantity) external payable nonReentrant {
        if (!publicMintEnabled) revert MintNotEnabled();
        if (_tokenIdCounter + quantity > MAX_SUPPLY) revert ExceedsMaxSupply();
        if (mintedCount[msg.sender] + quantity > MAX_PER_WALLET) revert ExceedsMaxPerWallet();

        uint256 cost = PUBLIC_PRICE * quantity;
        if (msg.value < cost) revert InsufficientPayment(cost, msg.value);

        mintedCount[msg.sender] += quantity;

        for (uint256 i = 0; i < quantity;) {
            _safeMint(msg.sender, _tokenIdCounter);
            unchecked {
                _tokenIdCounter++;
                i++;
            }
        }

        emit PublicMint(msg.sender, quantity);
    }

    /*//////////////////////////////////////////////////////////////
                            ADMIN FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    function setMerkleRoot(bytes32 merkleRoot_) external onlyOwner {
        merkleRoot = merkleRoot_;
    }

    function setWhitelistMintEnabled(bool enabled_) external onlyOwner {
        whitelistMintEnabled = enabled_;
    }

    function setPublicMintEnabled(bool enabled_) external onlyOwner {
        publicMintEnabled = enabled_;
    }

    function reveal(string memory baseURI_) external onlyOwner {
        revealed = true;
        _baseTokenURI = baseURI_;
        emit Revealed(baseURI_);
    }

    function withdraw() external onlyOwner nonReentrant {
        (bool success,) = payable(owner()).call{value: address(this).balance}("");
        if (!success) revert WithdrawalFailed();
    }

    /*//////////////////////////////////////////////////////////////
                            VIEW FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        _requireOwned(tokenId);

        if (!revealed) {
            return _hiddenMetadataURI;
        }

        return string(abi.encodePacked(_baseTokenURI, tokenId.toString(), ".json"));
    }

    function remainingSupply() external view returns (uint256) {
        return MAX_SUPPLY - _tokenIdCounter;
    }

    /*//////////////////////////////////////////////////////////////
                            REQUIRED OVERRIDES
    //////////////////////////////////////////////////////////////*/

    function _update(address to, uint256 tokenId, address auth)
        internal
        override(ERC721, ERC721Enumerable)
        returns (address)
    {
        return super._update(to, tokenId, auth);
    }

    function _increaseBalance(address account, uint128 value)
        internal
        override(ERC721, ERC721Enumerable)
    {
        super._increaseBalance(account, value);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Enumerable, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
