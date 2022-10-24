from brownie import reverts


def test_pausa_governance(voter_module, governance):
    voter_module.pause({"from": governance})
    assert voter_module.paused()


def test_unpause_guardian(voter_module, techops):
    with reverts("not-governance!"):
        voter_module.unpause({"from": techops})


def test_unpause_governance(voter_module, governance):
    voter_module.pause({"from": governance})
    assert voter_module.paused()
    voter_module.unpause({"from": governance})
    assert voter_module.paused() == False


def test_pause_guardian(voter_module, techops):
    voter_module.pause({"from": techops})
    assert voter_module.paused()


def test_pause_random_account(voter_module, accounts):
    with reverts("not-gov-or-guardian"):
        voter_module.pause({"from": accounts[6]})
