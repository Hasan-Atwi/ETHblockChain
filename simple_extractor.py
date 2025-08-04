"""
Simple Blockchain Data Extractor
Extracts only essential data: block headers, transactions, and basic token transfers/smart contract calls
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


class SimpleDataExtractor:
    """
    Simple data extractor for essential blockchain data only
    """
    
    def __init__(self, provider_url: str = None):
        """
        Initialize simple data extractor
        
        Args:
            provider_url: URL of the Ethereum provider (Infura, etc.)
        """
        if provider_url:
            self.provider_url = provider_url
        elif INFURA_URL and INFURA_URL != 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID':
            self.provider_url = INFURA_URL
        else:
            raise ValueError("No valid Infura URL found. Please set INFURA_URL in your environment variables.")
        
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
    
    def extract_block_headers(self, block_number: int) -> Optional[Dict[str, Any]]:
        """
        Extract block headers (essential block information)
        
        Args:
            block_number: Block number to extract
            
        Returns:
            Block header data or None if not found
        """
        try:
            # Get block without full transactions for efficiency
            block = self.w3.eth.get_block(block_number, full_transactions=False)
            
            return {
                'block_number': block['number'],
                'block_hash': block['hash'].hex(),
                'parent_hash': block['parentHash'].hex(),
                'timestamp': block['timestamp'],
                'miner': block['miner'],
                'difficulty': block['difficulty'],
                'gas_limit': block['gasLimit'],
                'gas_used': block['gasUsed'],
                'transaction_count': len(block['transactions']),
                'extra_data': block['extraData'].hex() if block['extraData'] else None
            }
        except BlockNotFound:
            logger.warning(f"Block {block_number} not found")
            return None
        except Exception as e:
            logger.error(f"Error extracting block headers for block {block_number}: {e}")
            return None
    
    def extract_transactions(self, block_number: int) -> List[Dict[str, Any]]:
        """
        Extract transactions from a block
        
        Args:
            block_number: Block number to extract transactions from
            
        Returns:
            List of transaction data
        """
        try:
            # Get block with full transactions
            block = self.w3.eth.get_block(block_number, full_transactions=True)
            
            transactions = []
            for tx in block['transactions']:
                tx_data = {
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
                transactions.append(tx_data)
            
            return transactions
            
        except BlockNotFound:
            logger.warning(f"Block {block_number} not found")
            return []
        except Exception as e:
            logger.error(f"Error extracting transactions for block {block_number}: {e}")
            return []
    
    def extract_basic_token_transfers(self, tx_hash: str) -> List[Dict[str, Any]]:
        """
        Extract basic token transfer information (simplified)
        
        Args:
            tx_hash: Transaction hash to analyze
            
        Returns:
            List of basic token transfer data
        """
        try:
            # Get transaction receipt
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            token_transfers = []
            
            # Check for any Transfer events (simplified approach)
            transfer_event_signature = self.w3.keccak(text="Transfer(address,address,uint256)").hex()
            
            for log in receipt['logs']:
                if len(log['topics']) >= 3 and log['topics'][0].hex() == transfer_event_signature:
                    # This is likely a token transfer
                    try:
                        # Simplified parsing - just get the raw data
                        token_transfer = {
                            'tx_hash': tx_hash,
                            'token_address': log['address'],
                            'from_address': '0x' + log['topics'][1].hex()[-40:],
                            'to_address': '0x' + log['topics'][2].hex()[-40:],
                            'raw_data': log['data'].hex(),  # Store raw data instead of parsing
                            'log_index': log['logIndex'],
                            'block_number': log['blockNumber']
                        }
                        token_transfers.append(token_transfer)
                    except Exception as e:
                        logger.warning(f"Error parsing token transfer in tx {tx_hash}: {e}")
                        continue
            
            return token_transfers
            
        except Exception as e:
            logger.error(f"Error extracting token transfers for tx {tx_hash}: {e}")
            return []
    
    def extract_basic_contract_calls(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Extract basic smart contract call information
        
        Args:
            tx_hash: Transaction hash to analyze
            
        Returns:
            Basic smart contract call data or None
        """
        try:
            # Get transaction details
            tx = self.w3.eth.get_transaction(tx_hash)
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            # Check if this is a contract interaction
            if tx['to'] and tx['input'] and tx['input'] != '0x':
                # This is likely a smart contract call
                contract_call = {
                    'tx_hash': tx_hash,
                    'contract_address': tx['to'],
                    'function_signature': tx['input'][:10] if len(tx['input']) >= 10 else None,
                    'input_data_length': len(tx['input']),
                    'gas_used': receipt['gasUsed'],
                    'status': receipt['status'],  # 1 = success, 0 = failed
                    'logs_count': len(receipt['logs']),
                    'block_number': tx['blockNumber']
                }
                return contract_call
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting smart contract call for tx {tx_hash}: {e}")
            return None
    
    def extract_block_data(self, block_number: int, include_token_transfers: bool = False, 
                          include_contract_calls: bool = False) -> Dict[str, Any]:
        """
        Extract complete block data with specified components
        
        Args:
            block_number: Block number to extract
            include_token_transfers: Whether to include token transfer analysis
            include_contract_calls: Whether to include smart contract call analysis
            
        Returns:
            Complete block data dictionary
        """
        # Extract block headers
        block_headers = self.extract_block_headers(block_number)
        if not block_headers:
            return None
        
        # Extract transactions
        transactions = self.extract_transactions(block_number)
        
        # Initialize result
        block_data = {
            'block_headers': block_headers,
            'transactions': transactions,
            'extraction_time': time.time()
        }
        
        # Optional: Extract basic token transfers
        if include_token_transfers:
            token_transfers = []
            for tx in transactions[:10]:  # Limit to first 10 for efficiency
                transfers = self.extract_basic_token_transfers(tx['tx_hash'])
                token_transfers.extend(transfers)
            block_data['token_transfers'] = token_transfers
        
        # Optional: Extract basic smart contract calls
        if include_contract_calls:
            contract_calls = []
            for tx in transactions[:10]:  # Limit to first 10 for efficiency
                call_data = self.extract_basic_contract_calls(tx['tx_hash'])
                if call_data:
                    contract_calls.append(call_data)
            block_data['smart_contract_calls'] = contract_calls
        
        return block_data
    
    def extract_block_range(self, start_block: int, end_block: int, 
                           include_token_transfers: bool = False,
                           include_contract_calls: bool = False) -> List[Dict[str, Any]]:
        """
        Extract data from a range of blocks
        
        Args:
            start_block: Starting block number
            end_block: Ending block number
            include_token_transfers: Whether to include token transfers
            include_contract_calls: Whether to include smart contract calls
            
        Returns:
            List of block data dictionaries
        """
        blocks_data = []
        
        for block_num in range(start_block, end_block + 1):
            logger.info(f"Extracting data from block {block_num}")
            
            block_data = self.extract_block_data(
                block_num, 
                include_token_transfers=include_token_transfers,
                include_contract_calls=include_contract_calls
            )
            
            if block_data:
                blocks_data.append(block_data)
            
            # Rate limiting to avoid API limits
            time.sleep(0.1)
        
        return blocks_data


# Example usage and testing
if __name__ == "__main__":
    # Test the simple data extractor
    extractor = SimpleDataExtractor()
    
    # Get latest block number
    latest_block = extractor.get_latest_block_number()
    print(f"Latest block number: {latest_block}")
    
    # Extract data from a recent block
    recent_block_num = latest_block - 1
    block_data = extractor.extract_block_data(
        recent_block_num,
        include_token_transfers=True,
        include_contract_calls=True
    )
    
    if block_data:
        headers = block_data['block_headers']
        transactions = block_data['transactions']
        
        print(f"\nBlock {headers['block_number']} Headers:")
        print(f"  Hash: {headers['block_hash'][:20]}...")
        print(f"  Timestamp: {headers['timestamp']}")
        print(f"  Transactions: {headers['transaction_count']}")
        print(f"  Gas Used: {headers['gas_used']:,}")
        
        print(f"\nTransactions: {len(transactions)}")
        if transactions:
            first_tx = transactions[0]
            print(f"  First TX: {first_tx['tx_hash'][:20]}...")
            print(f"  From: {first_tx['from_address']}")
            print(f"  To: {first_tx['to_address']}")
            print(f"  Value: {first_tx['value_ether']} ETH")
        
        if 'token_transfers' in block_data:
            print(f"\nToken Transfers: {len(block_data['token_transfers'])}")
        
        if 'smart_contract_calls' in block_data:
            print(f"\nSmart Contract Calls: {len(block_data['smart_contract_calls'])}") 