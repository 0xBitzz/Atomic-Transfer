from algosdk import account, mnemonic


class Account:
    def __init__(self):
        self._private_key = account.generate_account()[0]

    def _get_mnemonic(self):
        return mnemonic.from_private_key(self._private_key)


def get_mnemonics(num_of_accounts):
    account_details = {}
    for i in range(num_of_accounts):
        account_details[i] = Account()._get_mnemonic()
    return account_details
