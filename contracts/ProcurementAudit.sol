// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title ProcurementAudit
/// @notice Stores only SHA-256 record fingerprints - never proposals or evidence files.
contract ProcurementAudit {
    address public immutable administrator;
    mapping(bytes32 => uint256) public anchoredAt;

    event RecordAnchored(bytes32 indexed recordHash, uint256 timestamp, address indexed submittedBy);

    constructor() {
        administrator = msg.sender;
    }

    function anchorRecord(bytes32 recordHash) external {
        require(msg.sender == administrator, "Only the administrator may anchor records");
        require(anchoredAt[recordHash] == 0, "Record already anchored");
        anchoredAt[recordHash] = block.timestamp;
        emit RecordAnchored(recordHash, block.timestamp, msg.sender);
    }
}
