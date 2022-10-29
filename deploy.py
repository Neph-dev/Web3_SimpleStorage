from solcx import compile_standard
from web3 import Web3
from dotenv import load_dotenv
import json
import os

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# Compile our solidity
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)
# Store the compiled code into a json file.
with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]
# Get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# Connect to ganache
# w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
# chain_id = 1337
# my_address = "0x1484290e45238aD94ECed758cD840Ce55EBa0f95"
# private_key = os.getenv("PRIVATE_KEY")

# Connect to goerli
w3 = Web3(
    Web3.HTTPProvider("https://goerli.infura.io/v3/94148f9c00ba4b8d8842ad5db0d84138")
)
chain_id = 5
my_address = "0xc7FE04637fCAFb4466678136fbaF93f9ffcBe5d9"
private_key = os.getenv("PRIVATE_KEY")

# Create contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)
# Get the gas price
gas_price = w3.eth.gas_price

# 1. Build a transaction
# 2. Sign a transaction
# 2. Send signed transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {
        "gasPrice": gas_price,
        "chainId": chain_id,
        "from": my_address,
        "nonce": nonce,
    }
)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
print("Deploying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Contract deployed!")

# Working with the contract, we always need:
# Contract address;
# Contract abi.
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call -> Simulate making the call and getting a return value from
# Transact -> Actually make a state change.

# Initial value of favorite number
print("Initial favorite number value:", simple_storage.functions.retrieve().call())
print("Updating contract...")
store_transaction = simple_storage.functions.store(77).buildTransaction(
    {"gasPrice": gas_price, "chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
store_tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Contract updated!")
print("Updated favorite number value:", simple_storage.functions.retrieve().call())
