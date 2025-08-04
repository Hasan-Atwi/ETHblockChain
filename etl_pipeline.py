"""
ETL Pipeline Module
Extract, Transform, Load pipeline for blockchain data collection
"""

import logging
import time
import schedule
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from blockchain_client import BlockchainClient
from database import DatabaseManager
from config import BATCH_SIZE, START_BLOCK, END_BLOCK

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('blockchain_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ETLPipeline:
    """
    ETL Pipeline for blockchain data collection
    """
    
    def __init__(self, use_postgres: bool = True, use_mongodb: bool = True):
        """
        Initialize ETL pipeline
        
        Args:
            use_postgres: Whether to use PostgreSQL
            use_mongodb: Whether to use MongoDB
        """
        self.blockchain_client = BlockchainClient()
        self.db_manager = DatabaseManager(use_postgres=use_postgres, use_mongodb=use_mongodb)
        self.last_processed_block = self._get_last_processed_block()
        
        logger.info(f"ETL Pipeline initialized. Last processed block: {self.last_processed_block}")
    
    def _get_last_processed_block(self) -> int:
        """Get the last processed block number from database"""
        try:
            # Try to get the highest block number from database
            if self.db_manager.use_postgres:
                session = self.db_manager.PostgresSession()
                result = session.query(self.db_manager.Block.block_number).order_by(
                    self.db_manager.Block.block_number.desc()
                ).first()
                session.close()
                if result:
                    return result[0]
            
            # Fallback to MongoDB
            if self.db_manager.use_mongodb:
                result = self.db_manager.blocks_collection.find_one(
                    sort=[('block_number', -1)]
                )
                if result:
                    return result['block_number']
        except Exception as e:
            logger.error(f"Error getting last processed block: {e}")
        
        return START_BLOCK - 1
    
    def extract_blocks(self, start_block: int, end_block: int) -> List[Dict[str, Any]]:
        """
        Extract blocks from blockchain
        
        Args:
            start_block: Starting block number
            end_block: Ending block number
            
        Returns:
            List of block data
        """
        logger.info(f"Extracting blocks from {start_block} to {end_block}")
        
        blocks = []
        for block_num in range(start_block, end_block + 1):
            try:
                block_data = self.blockchain_client.get_block(block_num)
                if block_data:
                    blocks.append(block_data)
                    logger.debug(f"Extracted block {block_num}")
                else:
                    logger.warning(f"Block {block_num} not found or failed to extract")
                
                # Rate limiting to avoid API limits
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error extracting block {block_num}: {e}")
                continue
        
        logger.info(f"Successfully extracted {len(blocks)} blocks")
        return blocks
    
    def transform_block_data(self, block_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform block data for storage
        
        Args:
            block_data: Raw block data
            
        Returns:
            Transformed block data
        """
        # Add metadata
        block_data['extracted_at'] = datetime.utcnow().isoformat()
        block_data['data_source'] = 'ethereum_mainnet'
        
        # Ensure all required fields are present
        required_fields = [
            'block_number', 'block_hash', 'parent_hash', 'timestamp',
            'miner', 'difficulty', 'gas_limit', 'gas_used', 'transaction_count'
        ]
        
        for field in required_fields:
            if field not in block_data:
                logger.warning(f"Missing required field '{field}' in block {block_data.get('block_number', 'unknown')}")
                block_data[field] = None
        
        return block_data
    
    def transform_transaction_data(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform transaction data for storage
        
        Args:
            tx_data: Raw transaction data
            
        Returns:
            Transformed transaction data
        """
        # Add metadata
        tx_data['extracted_at'] = datetime.utcnow().isoformat()
        tx_data['data_source'] = 'ethereum_mainnet'
        
        # Ensure all required fields are present
        required_fields = [
            'tx_hash', 'block_number', 'from_address', 'to_address',
            'value_wei', 'value_ether', 'gas', 'gas_price', 'gas_price_gwei',
            'input_data', 'nonce', 'transaction_index'
        ]
        
        for field in required_fields:
            if field not in tx_data:
                logger.warning(f"Missing required field '{field}' in transaction {tx_data.get('tx_hash', 'unknown')}")
                tx_data[field] = None
        
        return tx_data
    
    def load_blocks(self, blocks: List[Dict[str, Any]]) -> int:
        """
        Load blocks into database
        
        Args:
            blocks: List of block data
            
        Returns:
            Number of successfully loaded blocks
        """
        logger.info(f"Loading {len(blocks)} blocks into database")
        
        success_count = 0
        for block_data in blocks:
            try:
                # Transform block data
                transformed_block = self.transform_block_data(block_data)
                
                # Store block
                logger.info(f"Storing block {block_data['block_number']} with {len(block_data.get('transactions', []))} transactions")
                if self.db_manager.store_block_with_transactions(transformed_block):
                    success_count += 1
                    logger.info(f"Successfully loaded block {block_data['block_number']} with {len(block_data.get('transactions', []))} transactions")
                else:
                    logger.error(f"Failed to load block {block_data['block_number']}")
                
            except Exception as e:
                logger.error(f"Error loading block {block_data.get('block_number', 'unknown')}: {e}")
                continue
        
        logger.info(f"Successfully loaded {success_count}/{len(blocks)} blocks")
        return success_count
    
    def process_block_range(self, start_block: int, end_block: int) -> Dict[str, Any]:
        """
        Process a range of blocks (Extract, Transform, Load)
        
        Args:
            start_block: Starting block number
            end_block: Ending block number
            
        Returns:
            Processing statistics
        """
        logger.info(f"Processing blocks from {start_block} to {end_block}")
        
        start_time = time.time()
        
        # Extract
        blocks = self.extract_blocks(start_block, end_block)
        
        if not blocks:
            logger.warning("No blocks extracted")
            return {
                'start_block': start_block,
                'end_block': end_block,
                'blocks_extracted': 0,
                'blocks_loaded': 0,
                'processing_time': time.time() - start_time,
                'success': False
            }
        
        # Load
        blocks_loaded = self.load_blocks(blocks)
        
        processing_time = time.time() - start_time
        
        stats = {
            'start_block': start_block,
            'end_block': end_block,
            'blocks_extracted': len(blocks),
            'blocks_loaded': blocks_loaded,
            'processing_time': processing_time,
            'success': blocks_loaded > 0
        }
        
        logger.info(f"Processing completed: {stats}")
        return stats
    
    def process_latest_blocks(self, num_blocks: int = BATCH_SIZE) -> Dict[str, Any]:
        """
        Process the latest blocks
        
        Args:
            num_blocks: Number of latest blocks to process
            
        Returns:
            Processing statistics
        """
        try:
            latest_block = self.blockchain_client.get_latest_block_number()
            start_block = max(self.last_processed_block + 1, latest_block - num_blocks + 1)
            end_block = latest_block
            
            if start_block > end_block:
                logger.info("No new blocks to process")
                return {
                    'start_block': start_block,
                    'end_block': end_block,
                    'blocks_extracted': 0,
                    'blocks_loaded': 0,
                    'processing_time': 0,
                    'success': True
                }
            
            stats = self.process_block_range(start_block, end_block)
            
            if stats['success']:
                self.last_processed_block = end_block
            
            return stats
            
        except Exception as e:
            logger.error(f"Error processing latest blocks: {e}")
            return {
                'start_block': 0,
                'end_block': 0,
                'blocks_extracted': 0,
                'blocks_loaded': 0,
                'processing_time': 0,
                'success': False,
                'error': str(e)
            }
    
    def process_historical_blocks(self, start_block: int = None, end_block: int = None) -> Dict[str, Any]:
        """
        Process historical blocks in batches
        
        Args:
            start_block: Starting block number (defaults to START_BLOCK)
            end_block: Ending block number (defaults to END_BLOCK or latest)
            
        Returns:
            Processing statistics
        """
        if start_block is None:
            start_block = START_BLOCK
        
        if end_block is None:
            if END_BLOCK > 0:
                end_block = END_BLOCK
            else:
                end_block = self.blockchain_client.get_latest_block_number()
        
        logger.info(f"Processing historical blocks from {start_block} to {end_block}")
        
        total_stats = {
            'total_blocks_extracted': 0,
            'total_blocks_loaded': 0,
            'total_processing_time': 0,
            'batches_processed': 0,
            'success': True
        }
        
        current_block = start_block
        
        while current_block <= end_block:
            batch_end = min(current_block + BATCH_SIZE - 1, end_block)
            
            logger.info(f"Processing batch: {current_block} to {batch_end}")
            
            batch_stats = self.process_block_range(current_block, batch_end)
            
            total_stats['total_blocks_extracted'] += batch_stats['blocks_extracted']
            total_stats['total_blocks_loaded'] += batch_stats['blocks_loaded']
            total_stats['total_processing_time'] += batch_stats['processing_time']
            total_stats['batches_processed'] += 1
            
            if not batch_stats['success']:
                total_stats['success'] = False
                logger.error(f"Batch processing failed for blocks {current_block} to {batch_end}")
            
            current_block = batch_end + 1
            
            # Update last processed block
            self.last_processed_block = batch_end
            
            # Small delay between batches
            time.sleep(1)
        
        logger.info(f"Historical processing completed: {total_stats}")
        return total_stats
    
    def run_scheduled_collection(self, interval_minutes: int = 5):
        """
        Run scheduled data collection
        
        Args:
            interval_minutes: Collection interval in minutes
        """
        logger.info(f"Starting scheduled collection every {interval_minutes} minutes")
        
        def collect_latest_data():
            try:
                stats = self.process_latest_blocks()
                logger.info(f"Scheduled collection completed: {stats}")
            except Exception as e:
                logger.error(f"Error in scheduled collection: {e}")
        
        # Schedule the job
        schedule.every(interval_minutes).minutes.do(collect_latest_data)
        
        # Run the scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def close(self):
        """Close connections"""
        self.db_manager.close()
        logger.info("ETL Pipeline connections closed")


# Example usage and testing
if __name__ == "__main__":
    # Test the ETL pipeline
    pipeline = ETLPipeline(use_postgres=False, use_mongodb=True)  # Use only MongoDB for testing
    
    try:
        # Process latest blocks
        print("Processing latest blocks...")
        stats = pipeline.process_latest_blocks(num_blocks=5)
        print(f"Latest blocks processing stats: {stats}")
        
        # Process historical blocks (small range for testing)
        print("\nProcessing historical blocks...")
        latest_block = pipeline.blockchain_client.get_latest_block_number()
        historical_stats = pipeline.process_historical_blocks(
            start_block=latest_block - 10,
            end_block=latest_block - 5
        )
        print(f"Historical processing stats: {historical_stats}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
    
    finally:
        pipeline.close() 