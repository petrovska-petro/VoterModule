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
def techops(accounts):
    # # https://github.com/Badger-Finance/badger-multisig/blob/main/helpers/addresses.py#L50
    return accounts.at("0x86cbD0ce0c087b482782c181dA8d191De18C8275", force=True)


@pytest.fixture
def trops(accounts):
    # https://github.com/Badger-Finance/badger-multisig/blob/main/helpers/addresses.py#L55
    return accounts.at("0x042B32Ac6b453485e357938bdC38e0340d4b9276", force=True)


@pytest.fixture
def keeper():
    # https://docs.chain.link/docs/chainlink-automation/supported-networks/#registry-and-registrar-addresses
    return accounts.at("0x02777053d6764996e594c3E88AF1D58D5363a2e6", force=True)


@pytest.fixture
def safe():
    # https://github.com/Badger-Finance/badger-multisig/blob/main/helpers/addresses.py#L58
    return interface.IGnosisSafe("0xA9ed98B5Fb8428d68664f3C5027c62A10d45826b")


@pytest.fixture
def voter_module(deployer, governance):
    return VoterModule.deploy(governance, chain.time(), HOUR_SECS, {"from": deployer})


# https://docs.pytest.org/en/6.2.x/fixture.html#autouse-fixtures-fixtures-you-don-t-have-to-request
@pytest.fixture(autouse=True)
def config_module(safe, voter_module, governance, techops, keeper):
    # enable module
    safe.enableModule(voter_module.address, {"from": safe})
    assert voter_module.address in safe.getModules()

    # add executors. roles i expect: techops & CL keepers
    voter_module.addExecutor(techops, {"from": governance})
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
