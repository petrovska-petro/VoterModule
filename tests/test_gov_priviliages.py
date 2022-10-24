from brownie import reverts


def test_add_executor(voter_module, governance, accounts):
    voter_module.addExecutor(accounts[3], {"from": governance})
    assert accounts[3] in voter_module.getExecutors()


def test_add_executor_random_account(voter_module, accounts):
    with reverts("not-governance!"):
        voter_module.addExecutor(accounts[3], {"from": accounts[6]})


def test_remove_executor(voter_module, governance, accounts):
    voter_module.addExecutor(accounts[3], {"from": governance})
    assert accounts[3] in voter_module.getExecutors()
    voter_module.removeExecutor(accounts[3], {"from": governance})
    assert accounts[3] not in voter_module.getExecutors()


def test_remove_executor_random_account(voter_module, accounts):
    with reverts("not-governance!"):
        voter_module.removeExecutor(accounts[3], {"from": accounts[6]})


def test_set_guardian(voter_module, governance, accounts):
    voter_module.setGuardian(accounts[3], {"from": governance})
    assert voter_module.guardian() == accounts[3]


def test_set_guardian_random_account(voter_module, accounts):
    with reverts("not-governance!"):
        voter_module.setGuardian(accounts[3], {"from": accounts[6]})
