// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@chainlink/contracts/src/v0.8/KeeperCompatible.sol";

import "interfaces/gnosis/IGnosisSafe.sol";
import "interfaces/aura/ILockAura.sol";
import "interfaces/badger/IGravi.sol";

/// @title   VoterModule
/// @author  Petrovska @ BadgerDAO
/// @dev  Allows whitelisted executors to trigger `performUpkeep` with limited scoped
/// in our case to carry voter weekly chores
/// Inspired from: https://github.com/gnosis/zodiac-guard-scope
contract VoterModule is KeeperCompatibleInterface, Pausable {
    using EnumerableSet for EnumerableSet.AddressSet;

    /* ========== CONSTANTS VARIABLES ========== */
    IGnosisSafe public constant SAFE =
        IGnosisSafe(0xA9ed98B5Fb8428d68664f3C5027c62A10d45826b);
    IERC20 public constant AURA =
        IERC20(0xC0c293ce456fF0ED870ADd98a0828Dd4d2903DBF);
    IERC20 public constant AURABAL =
        IERC20(0x616e8BfA43F920657B3497DBf40D6b1A02D4608d);
    ILockAura public constant LOCKER =
        ILockAura(0x3Fa73f1E5d8A792C80F426fc8F84FBF7Ce9bBCAC);
    IGravi constant GRAVI = IGravi(0xBA485b556399123261a5F9c95d413B4f93107407);
    address constant TROPS = 0x042B32Ac6b453485e357938bdC38e0340d4b9276;

    /* ========== STATE VARIABLES ========== */
    address public governance;
    uint256 public lastTimestamp;
    uint256 public interval;

    EnumerableSet.AddressSet internal _executors;

    /// @dev address target allowed to trigger
    mapping(address => bool) public allowedTargets;

    /* ========== EVENT ========== */
    event SetTargetAllowed(address target, bool allowed);

    constructor(
        address _governance,
        uint64 _startTimestamp,
        uint256 _intervalSeconds
    ) {
        governance = _governance;
        lastTimestamp = _startTimestamp;
        interval = _intervalSeconds;
    }

    /***************************************
                    MODIFIERS
    ****************************************/
    modifier onlyGovernance() {
        require(msg.sender == governance, "not-governance!");
        _;
    }

    modifier onlyExecutors() {
        require(_executors.contains(msg.sender), "not-executor!");
        _;
    }

    /***************************************
               ADMIN - GOVERNANCE
    ****************************************/
    /// @dev Set whether or not calls can be made to an address.
    /// @notice Only callable by governance.
    /// @param target Address to be allowed/disallowed.
    /// @param allow Bool to allow (true) or disallow (false) calls to target.
    function setTargetAllowed(address target, bool allow)
        external
        onlyGovernance
    {
        allowedTargets[target] = allow;
        emit SetTargetAllowed(target, allowedTargets[target]);
    }

    /// @dev Adds an executor to the Set of allowed addresses.
    /// @notice Only callable by governance.
    /// @param _executor Address which will have rights to call `checkTransactionAndExecute`.
    function addExecutor(address _executor) external onlyGovernance {
        require(_executor != address(0), "zero-address!");
        _executors.add(_executor);
    }

    /// @dev Removes an executor to the Set of allowed addresses.
    /// @notice Only callable by governance.
    /// @param _executor Address which will not have rights to call `checkTransactionAndExecute`.
    function removeExecutor(address _executor) external onlyGovernance {
        require(_executor != address(0), "zero-address!");
        _executors.remove(_executor);
    }

    /// @dev Updates the governance address
    /// @notice Only callable by governance.
    /// @param _governance Address which will beccome governance
    function setGovernance(address _governance) external onlyGovernance {
        governance = _governance;
    }

    /***************************************
                KEEPERS - EXECUTORS
    ****************************************/
    /// @dev Runs off-chain at every block to determine if the `performUpkeep`
    /// function should be called on-chain.
    function checkUpkeep(bytes calldata)
        external
        view
        override
        whenNotPaused
        returns (bool upkeepNeeded, bytes memory checkData)
    {
        upkeepNeeded = (block.timestamp - lastTimestamp) > interval;
    }

    /// @dev Contains the logic that should be executed on-chain when
    /// `checkUpkeep` returns true.
    function performUpkeep(bytes calldata performData)
        external
        override
        onlyExecutors
        whenNotPaused
    {
        /// @dev double check the time interval in the perform block
        if ((block.timestamp - lastTimestamp) > interval) {
            // 1. process unlocks
            _processExpiredLocks();
            // 2. claim vlaura rewards and transfer aurabal to trops
            _claimRewardsAndSweep();
            // 3. wd gravi and lock aura in voter
            _withdrawGraviAndLockAura();
            // 4. update last ts
            lastTimestamp = block.timestamp;
        }
    }

    /// @dev method will process expired locks if available
    function _processExpiredLocks() internal {
        (, uint256 unlockable, , ) = LOCKER.lockedBalances(address(SAFE));
        if (unlockable > 0) {
            _checkTransactionAndExecute(
                address(LOCKER),
                abi.encodeWithSelector(
                    ILockAura.processExpiredLocks.selector,
                    true
                )
            );
        }
    }

    /// @dev method will claim auraBAL & transfer balance to trops
    function _claimRewardsAndSweep() internal {
        (, uint256 rewards) = LOCKER.userData(address(SAFE), address(AURABAL));
        if (rewards > 0) {
            _checkTransactionAndExecute(
                address(LOCKER),
                abi.encodeWithSelector(
                    ILockAura.getReward.selector,
                    address(SAFE)
                )
            );
            _checkTransactionAndExecute(
                address(AURABAL),
                abi.encodeWithSelector(
                    IERC20.transfer.selector,
                    TROPS,
                    AURABAL.balanceOf(address(SAFE))
                )
            );
        }
    }

    /// @dev method will wd from graviaura and lock aura in voter msig
    function _withdrawGraviAndLockAura() internal {
        if (GRAVI.balanceOf(address(SAFE)) > 0) {
            _checkTransactionAndExecute(
                address(GRAVI),
                abi.encodeWithSelector(IGravi.withdrawAll.selector)
            );

            uint256 auraSafeBal = AURA.balanceOf(address(SAFE));
            if (auraSafeBal > 0) {
                /// @dev approves aura to process in locker
                _checkTransactionAndExecute(
                    address(AURA),
                    abi.encodeWithSelector(
                        IERC20.approve.selector,
                        address(LOCKER),
                        auraSafeBal
                    )
                );
                /// @dev lock aura in locker
                _checkTransactionAndExecute(
                    address(LOCKER),
                    abi.encodeWithSelector(
                        ILockAura.lock.selector,
                        address(SAFE),
                        auraSafeBal
                    )
                );
            }
        }
    }

    /// @dev Allows executing specific calldata into an address thru a gnosis-safe, which have enable this contract as module.
    /// @notice Only callable by executors.
    /// @param to Contract address where we will execute the calldata.
    /// @param data Calldata to be executed within the boundaries of the `allowedFunctions`.
    function _checkTransactionAndExecute(address to, bytes memory data)
        internal
    {
        require(allowedTargets[to], "address-not-allowed!");

        if (data.length >= 4) {
            require(
                SAFE.execTransactionFromModule(
                    to,
                    0,
                    data,
                    IGnosisSafe.Operation.Call
                ),
                "exec-error!"
            );
        }
    }
}
