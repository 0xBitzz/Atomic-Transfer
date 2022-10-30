import json
from account import get_mnemonics
from algosdk import mnemonic
from algosdk.v2client import algod
from algosdk.future.transaction import *


class AtomicTransfer:
    def __init__(self):
        algod_token = "a" * 64
        algod_address = "http://localhost:4001"
        self.client = algod.AlgodClient(algod_token, algod_address)

    def get_account_balance(self, address):
        return self.client.account_info(address)["amount"]

    def group_transaction(self):
        mnemonics_dict = get_mnemonics(3)

        account1 = mnemonic.to_public_key(mnemonics_dict[0])
        account2 = mnemonic.to_public_key(mnemonics_dict[1])
        account3 = mnemonic.to_public_key(mnemonics_dict[2])

        sk1 = mnemonic.to_private_key(mnemonics_dict[0])
        sk2 = mnemonic.to_private_key(mnemonics_dict[1])

        print(f"Account1 initial balance {self.get_account_balance(account1)}")
        print(f"Account2 initial balance {self.get_account_balance(account2)}")
        print(f"Account3 initial balance {self.get_account_balance(account3)}")

        input(f"Go to https://app.dappflow.org/dispenser and fund this address {account1}, then hit enter")
        input(f"Go to https://app.dappflow.org/dispenser and fund this address {account2}, then hit enter")

        params = self.client.suggested_params()

        # Txn from account1 to account3
        print("Creating transactions")
        sender = account1
        receiver = account3
        amount = 100000
        txn1 = PaymentTxn(sender, params, receiver, amount)
        print(f"Sending {amount} microAlgos from {sender} to {receiver}")
        print(f"Created txn: {txn1.get_txid()}")

        # Txn from account 2 to account 1
        sender = account2
        receiver = account1
        amount = 200000
        txn2 = PaymentTxn(sender, params, receiver, amount)
        print(f"Sending {amount} microAlgos from {sender} to {receiver}")
        print(f"Created txn: {txn2.get_txid()}")

        # Compute group id and put it into each transaction
        print("Grouping transactions")
        gid = transaction.calculate_group_id([txn1, txn2])
        print(f"Computed group id: {gid}")
        txn1.group = gid
        txn2.group = gid

        # Sign transactions
        stxn1 = txn1.sign(sk1)
        print(f"Account1 signed transaction: {stxn1}")
        stxn2 = txn2.sign(sk2)
        print(f"Account2 signed transaction: {stxn2}")

        # Assemble transactions
        print("Assembling transaction group")
        signed_group = [stxn1, stxn2]

        # Send transaction group
        txid = self.client.send_transactions(signed_group)

        # Wait for confirmation
        confirmed_txn = wait_for_confirmation(self.client, txid, 4)
        print(f"{txid} confirmed in round {confirmed_txn['confirmed-round']}")

        # Display account balances
        print(self.get_account_balance(account1))
        print(self.get_account_balance(account2))
        print(self.get_account_balance(account3))

        # Display confirmed transaction group
        confirmed_txn = self.client.pending_transaction_info(txn1.get_txid())
        print(f"Transaction info: {json.dumps(confirmed_txn, indent=4)}")

        confirmed_txn = self.client.pending_transaction_info(txn2.get_txid())
        print(f"Transaction info: {json.dumps(confirmed_txn, indent=4)}")


atomic_transfer = AtomicTransfer()
atomic_transfer.group_transaction()
