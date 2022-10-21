from brownie import chain, reverts


def test_upkeep_needed(voter_module, keeper):
    upkeep_needed, _ = voter_module.checkUpkeep(b"", {"from": keeper})
    assert upkeep_needed
    return upkeep_needed


def test_perform_upkeep_cl_keeper(
    voter_module, keeper, safe, gravi, aura, aurabal, trops, aura_locker
):
    # push time for trigger `True` in upkeep
    target_ts = voter_module.lastRewardClaimTimestamp() + voter_module.interval() * 2
    chain.mine(timestamp=target_ts)
    upkeep_needed = test_upkeep_needed(voter_module, keeper)
    assert upkeep_needed

    # check vals before
    aurabal_bal_before = aurabal.balanceOf(trops)
    gravi_bal_before = gravi.balanceOf(safe)

    # exec voter chore
    tx = voter_module.performUpkeep(b"", {"from": keeper})

    # check new custom event to including timestamp
    assert len(tx.events["RewardPaidModule"]) > 0
    print(tx.events["RewardPaidModule"])

    # check that unlocks all were processed
    _, unlockable, _, _ = aura_locker.lockedBalances(safe)
    assert unlockable == 0
    # check that aurabal in trops increased
    aurabal_bal_after = aurabal.balanceOf(trops)
    assert aurabal_bal_after > aurabal_bal_before
    # check that gravi is same value or less. Same if nothing could be wd
    gravi_bal_after = gravi.balanceOf(safe)
    assert gravi_bal_after <= gravi_bal_before
    # check that naked aura is zero
    assert aura.balanceOf(safe) == 0


def test_perform_upkeep_techops(
    voter_module, techops, safe, gravi, aura, aurabal, trops, aura_locker
):
    # push time for trigger `True` in upkeep
    target_ts = voter_module.lastRewardClaimTimestamp() + voter_module.interval() * 2
    chain.mine(timestamp=target_ts)
    upkeep_needed = test_upkeep_needed(voter_module, techops)
    assert upkeep_needed

    # check vals before
    aurabal_bal_before = aurabal.balanceOf(trops)
    gravi_bal_before = gravi.balanceOf(safe)

    # exec voter chore
    voter_module.performUpkeep(b"", {"from": techops})

    # check that unlocks all were processed
    _, unlockable, _, _ = aura_locker.lockedBalances(safe)
    assert unlockable == 0
    # check that aurabal in trops increased, here may be equal since already was claim once
    aurabal_bal_after = aurabal.balanceOf(trops)
    assert aurabal_bal_after >= aurabal_bal_before
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
