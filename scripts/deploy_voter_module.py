from brownie import VoterModule, accounts


MONTH_SECONDS = 2630000


def main(deployer_label=None):
    deployer = accounts.load(deployer_label)

    # NOTE: last auraBAL harvest tx
    # https://etherscan.io/tx/0xce85833f4ab307949f1c0758b09ed3fe97571780411276f4d050f980472d99c2
    return VoterModule.deploy(
        "0x86cbD0ce0c087b482782c181dA8d191De18C8275",  # https://github.com/Badger-Finance/badger-multisig/blob/main/helpers/addresses.py#L50
        1666372103,
        MONTH_SECONDS,
        {"from": deployer},
        publish_source=True,
    )
