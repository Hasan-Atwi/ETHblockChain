from web3 import Web3

# Connect to Infura
infura_url = "https://mainnet.infura.io/v3/YOUR_PROJECT_ID"
w3 = Web3(Web3.HTTPProvider(infura_url))

# Test connection
print("Connected:", w3.is_connected())

# Get latest block
latest_block = w3.eth.get_block('latest', full_transactions=True)

print("Block Number:", latest_block.number)
print("Transactions in Block:", len(latest_block.transactions))

# Example: Print first transaction details
if latest_block.transactions:
    tx = latest_block.transactions[0]
    print("From:", tx['from'])
    print("To:", tx['to'])
    print("Value (ETH):", w3.from_wei(tx['value'], 'ether'))
