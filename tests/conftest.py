import pytest
from brownie import chain, accounts, interface, VoterModule

HOUR_SECS = 3600


@pytest.fixture
def deployer(accounts):
    return accounts[0]


@pytest.fixture
def governance(accounts):
    return accounts[1]


@pytest.fixture
def executor(accounts):
    return accounts[2]


@pytest.fixture
def trops(accounts):
    return accounts.at("0x042B32Ac6b453485e357938bdC38e0340d4b9276", force=True)


@pytest.fixture
def keeper():
    return accounts.at("0x02777053d6764996e594c3E88AF1D58D5363a2e6", force=True)


@pytest.fixture
def safe():
    # voter_msig
    return interface.IGnosisSafe("0xA9ed98B5Fb8428d68664f3C5027c62A10d45826b")


@pytest.fixture
def voter_module(deployer, governance):
    return VoterModule.deploy(governance, chain.time(), HOUR_SECS, {"from": deployer})


@pytest.fixture(autouse=True)
def config_module(safe, voter_module, governance, executor, keeper):
    # enable module
    safe.enableModule(voter_module.address, {"from": safe})
    assert voter_module.address in safe.getModules()

    # add executor
    voter_module.addExecutor(executor, {"from": governance})
    voter_module.addExecutor(keeper, {"from": governance})


@pytest.fixture()
def gravi():
    return interface.ERC20("0xBA485b556399123261a5F9c95d413B4f93107407")


@pytest.fixture()
def aura():
    return interface.ERC20("0xC0c293ce456fF0ED870ADd98a0828Dd4d2903DBF")


@pytest.fixture()
def aurabal():
    return interface.ERC20("0x616e8BfA43F920657B3497DBf40D6b1A02D4608d")


@pytest.fixture()
def aura_locker():
    return interface.ILockAura("0x3Fa73f1E5d8A792C80F426fc8F84FBF7Ce9bBCAC")
