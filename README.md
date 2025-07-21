# ETHblockChain

A Python-based Ethereum blockchain interaction project that demonstrates how to connect to the Ethereum mainnet and retrieve blockchain data.

## Tech Stack

### Programming Language
- **Python 3.x** - Main programming language

### Libraries & Dependencies
- **web3.py** - Python library for interacting with Ethereum blockchain
  - Used for connecting to Ethereum nodes
  - Retrieving block and transaction data
  - Converting Wei to Ether values

### External Services
- **Infura** - Ethereum node provider
  - Provides HTTP endpoint for Ethereum mainnet access
  - Eliminates the need to run a local Ethereum node

## Features

- Connect to Ethereum mainnet via Infura
- Retrieve latest block information
- Display block number and transaction count
- Extract and display transaction details (from, to, value)
- Convert Wei values to Ether for readability

## Setup

1. Install required dependencies:
   ```bash
   pip install web3
   ```

2. Get an Infura project ID:
   - Sign up at [Infura.io](https://infura.io/)
   - Create a new project
   - Copy your project ID

3. Update the `infura_url` in `learning.py` with your project ID:
   ```python
   infura_url = "https://mainnet.infura.io/v3/YOUR_PROJECT_ID"
   ```

## Usage

Run the main script:
```bash
python learning.py
```

The script will:
- Test the connection to Ethereum mainnet
- Fetch the latest block
- Display block information and first transaction details

## Project Structure

```
ETHblockChain/
├── learning.py          # Main script for blockchain interaction
├── .gitignore          # Git ignore file
└── README.md           # Project documentation
```

## Requirements

- Python 3.6+
- Internet connection for Infura API access
- Valid Infura project ID

## License

This project is for educational purposes to learn Ethereum blockchain interaction with Python.