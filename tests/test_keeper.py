from brownie import chain


def test_upkeep_needed(voter_module, keeper):
    upkeep_needed, _ = voter_module.checkUpkeep(b"", {"from": keeper})
    assert upkeep_needed
    return upkeep_needed


def test_perform_upkeep(
    voter_module, keeper, safe, gravi, aura, aurabal, trops, aura_locker
):
    upkeep_needed = test_upkeep_needed(voter_module, keeper)
    assert upkeep_needed
    
    # check vals before
    aurabal_bal_before = aurabal.balanceOf(trops)
    gravi_bal_before = gravi.balanceOf(safe)

    # exec voter chore + summing interval for aurabal processing
    chain.sleep(voter_module.interval())
    chain.mine()
    voter_module.performUpkeep(b"", {"from": keeper})

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
