// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

interface IGravi {
    function withdrawAll() external;

    function balanceOf(address account) external view returns (uint256);
}
