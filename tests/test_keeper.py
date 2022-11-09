from brownie import chain, reverts, accounts

## Bal vault
GRAVI_WHALE = "0xba12222222228d8ba445958a75a0704d566bf2c8"


def is_upkeep_needed(voter_module, keeper):
    upkeep_needed, _ = voter_module.checkUpkeep(b"", {"from": keeper})
    assert upkeep_needed
    return upkeep_needed


def test_perform_upkeep_keeper(
    voter_module, keeper, safe, gravi, aura, aurabal, trops, aura_locker
):
    # push time for trigger `True` in upkeep
    target_ts = (
        voter_module.lastRewardClaimTimestamp() + voter_module.claimingInterval() * 2
    )
    chain.mine(timestamp=target_ts)
    upkeep_needed = is_upkeep_needed(voter_module, keeper)
    assert upkeep_needed

    ## Donate some graviAura to test locking as well
    gravi.transfer(safe, 1e18, {"from": accounts.at(GRAVI_WHALE, force=True)})

    # check vals before
    aurabal_bal_before = aurabal.balanceOf(trops)
    gravi_bal_before = gravi.balanceOf(safe)

    # check that unlocks all were processed
    _, _, beforeLocked, _ = aura_locker.lockedBalances(safe)

    # exec voter chore
    tx = voter_module.performUpkeep(b"", {"from": keeper})

    # check new custom event to including timestamp
    reward_paid_event = tx.events["RewardPaid"]
    assert len(reward_paid_event) > 0
    print(reward_paid_event)

    # check that unlocks all were processed
    _, unlockable, afterLocked, _ = aura_locker.lockedBalances(safe)
    ## We did lock something
    assert afterLocked - beforeLocked > 0
    ## We have unlocked all old stuf
    assert unlockable == 0
    # check that aurabal in trops increased
    aurabal_bal_after = aurabal.balanceOf(trops)
    assert aurabal_bal_after > aurabal_bal_before
    # check that gravi is same value or less. Same if nothing could be wd
    gravi_bal_after = gravi.balanceOf(safe)
    assert gravi_bal_after <= gravi_bal_before
    # check that naked aura is zero
    assert aura.balanceOf(safe) == 0


def test_perform_upkeep_paused_state(voter_module, keeper, governance):
    voter_module.pause({"from": governance})
    with reverts("Pausable: paused"):
        voter_module.performUpkeep(b"", {"from": keeper})
    voter_module.unpause({"from": governance})


def test_perform_upkeep_from_random_account(voter_module, keeper, accounts):
    with reverts("not-executor!"):
        voter_module.performUpkeep(b"", {"from": accounts[6]})
