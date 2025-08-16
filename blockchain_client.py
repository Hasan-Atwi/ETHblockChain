"""
Blockchain Client Module
Handles connections to Ethereum blockchain and data extraction
"""

import logging
from web3 import Web3
from web3.exceptions import BlockNotFound, TransactionNotFound
import time
from typing import Dict, List, Optional, Any
from config import INFURA_URL

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlockchainClient:
    """
    Client for interacting with Ethereum blockchain
    """
    
    def __init__(self, provider_url: str = None):
        """
        Initialize blockchain client
        
        Args:
            provider_url: URL of the Ethereum provider (Infura, etc.)
        """
        if provider_url:
            self.provider_url = provider_url
        elif INFURA_URL and INFURA_URL != 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID':
            self.provider_url = INFURA_URL
        else:
            raise ValueError("No valid Infura URL found. Please set INFURA_URL in your environment variables with your Infura Project ID.")
        
        self.w3 = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Ethereum network"""
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.provider_url))
            if self.w3.is_connected():
                logger.info(f"Successfully connected to Ethereum network via {self.provider_url}")
                logger.info(f"Current block number: {self.w3.eth.block_number}")
            else:
                raise ConnectionError("Failed to connect to Ethereum network")
        except Exception as e:
            logger.error(f"Error connecting to Ethereum network: {e}")
            raise
    
    def get_latest_block_number(self) -> int:
        """Get the latest block number"""
        try:
            return self.w3.eth.block_number
        except Exception as e:
            logger.error(f"Error getting latest block number: {e}")
            raise
    
    def get_block(self, block_number: int, include_transactions: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get block data by block number
        
        Args:
            block_number: Block number to retrieve
            include_transactions: Whether to include full transaction data
            
        Returns:
            Block data dictionary or None if not found
        """
        try:
            block = self.w3.eth.get_block(block_number, full_transactions=include_transactions)
            
            # DEBUG: Log transaction retrieval details
            if include_transactions:
                tx_count = len(block.get('transactions', []))
                logger.info(f"DEBUG: Block {block_number} retrieved with {tx_count} transactions")
                if tx_count > 0:
                    first_tx = block['transactions'][0]
                    # Treat Web3 AttributeDict like a mapping
                    if hasattr(first_tx, 'get'):
                        logger.info(f"DEBUG: First transaction is full object with hash: {first_tx.get('hash', 'N/A')}")
                    else:
                        logger.warning(f"DEBUG: First transaction is just a hash: {first_tx}")
                else:
                    logger.info(f"DEBUG: Block {block_number} contains no transactions")
            
            return self._format_block_data(block)
        except BlockNotFound:
            logger.warning(f"Block {block_number} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting block {block_number}: {e}")
            return None
    
    def get_block_range(self, start_block: int, end_block: int) -> List[Dict[str, Any]]:
        """
        Get multiple blocks in a range
        
        Args:
            start_block: Starting block number
            end_block: Ending block number
            
        Returns:
            List of block data dictionaries
        """
        blocks = []
        for block_num in range(start_block, end_block + 1):
            block_data = self.get_block(block_num)
            if block_data:
                blocks.append(block_data)
            time.sleep(0.1)  # Rate limiting to avoid API limits
        return blocks
    
    def get_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get transaction data by hash
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            Transaction data dictionary or None if not found
        """
        try:
            tx = self.w3.eth.get_transaction(tx_hash)
            return self._format_transaction_data(tx)
        except TransactionNotFound:
            logger.warning(f"Transaction {tx_hash} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting transaction {tx_hash}: {e}")
            return None
    
    def _format_block_data(self, block) -> Dict[str, Any]:
        """
        Format raw block data into a structured dictionary
        
        Args:
            block: Raw block data from Web3
            
        Returns:
            Formatted block data
        """
        formatted_block = {
            'block_number': block['number'],
            'block_hash': block['hash'].hex(),
            'parent_hash': block['parentHash'].hex(),
            'timestamp': block['timestamp'],
            'miner': block['miner'],
            'difficulty': block['difficulty'],
            'gas_limit': block['gasLimit'],
            'gas_used': block['gasUsed'],
            'transaction_count': len(block['transactions']),
        }
        
        # Only format transactions if they are full transaction objects (not just hashes)
        if block['transactions'] and len(block['transactions']) > 0 and hasattr(block['transactions'][0], 'get'):
            formatted_block['transactions'] = [self._format_transaction_data(tx) for tx in block['transactions']]
        else:
            # If transactions are just hashes or empty, don't include them
            formatted_block['transactions'] = []
            
        return formatted_block
    
    def _format_transaction_data(self, tx) -> Dict[str, Any]:
        """
        Format raw transaction data into a structured dictionary
        
        Args:
            tx: Raw transaction data from Web3
            
        Returns:
            Formatted transaction data
        """
        return {
            'tx_hash': tx['hash'].hex(),
            'block_number': tx['blockNumber'],
            'from_address': tx['from'],
            'to_address': tx['to'],
            'value_wei': tx['value'],
            'value_ether': self.w3.from_wei(tx['value'], 'ether'),
            'gas': tx['gas'],
            'gas_price': tx['gasPrice'],
            'gas_price_gwei': self.w3.from_wei(tx['gasPrice'], 'gwei'),
            'input_data': tx['input'],
            'nonce': tx['nonce'],
            'transaction_index': tx['transactionIndex']
        }
    
    def get_eth_balance(self, address: str) -> float:
        """
        Get ETH balance for an address
        
        Args:
            address: Ethereum address
            
        Returns:
            Balance in ETH
        """
        try:
            balance_wei = self.w3.eth.get_balance(address)
            return self.w3.from_wei(balance_wei, 'ether')
        except Exception as e:
            logger.error(f"Error getting balance for {address}: {e}")
            raise
    
    def is_address_valid(self, address: str) -> bool:
        """
        Check if an Ethereum address is valid
        
        Args:
            address: Ethereum address to validate
            
        Returns:
            True if valid, False otherwise
        """
        return self.w3.is_address(address)


# Example usage and testing
if __name__ == "__main__":
    # Test the blockchain client
    client = BlockchainClient()
    
    # Get latest block
    latest_block_num = client.get_latest_block_number()
    print(f"Latest block number: {latest_block_num}")
    
    # Get a recent block
    recent_block = client.get_block(latest_block_num - 1)
    if recent_block:
        print(f"Block {recent_block['block_number']} has {recent_block['transaction_count']} transactions")
        
        # Show first transaction details
        if recent_block['transactions']:
            first_tx = recent_block['transactions'][0]
            print(f"First transaction: {first_tx['tx_hash'][:20]}...")
            print(f"From: {first_tx['from_address']}")
            print(f"To: {first_tx['to_address']}")
            print(f"Value: {first_tx['value_ether']} ETH") 