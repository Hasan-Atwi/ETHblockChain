"""
Database Module
Handles database connections and operations for storing blockchain data
"""

import logging
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from datetime import datetime
import json
from config import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD,
    MONGODB_URI, MONGODB_DB
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy setup
Base = declarative_base()


class Block(Base):
    """PostgreSQL model for blocks"""
    __tablename__ = 'blocks'
    
    block_number = Column(BigInteger, primary_key=True)
    block_hash = Column(String(66), unique=True, nullable=False)
    parent_hash = Column(String(66), nullable=False)
    timestamp = Column(BigInteger, nullable=False)
    miner = Column(String(42), nullable=False)
    difficulty = Column(BigInteger, nullable=False)
    gas_limit = Column(BigInteger, nullable=False)
    gas_used = Column(BigInteger, nullable=False)
    transaction_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Transaction(Base):
    """PostgreSQL model for transactions"""
    __tablename__ = 'transactions'
    
    tx_hash = Column(String(66), primary_key=True)
    block_number = Column(BigInteger, nullable=False)
    from_address = Column(String(42), nullable=False)
    to_address = Column(String(42), nullable=True)
    value_wei = Column(BigInteger, nullable=False)
    value_ether = Column(Float, nullable=False)
    gas = Column(BigInteger, nullable=False)
    gas_price = Column(BigInteger, nullable=False)
    gas_price_gwei = Column(Float, nullable=False)
    input_data = Column(Text, nullable=True)
    nonce = Column(BigInteger, nullable=False)
    transaction_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, use_postgres: bool = True, use_mongodb: bool = True):
        """
        Initialize database manager
        
        Args:
            use_postgres: Whether to use PostgreSQL
            use_mongodb: Whether to use MongoDB
        """
        self.use_postgres = use_postgres
        self.use_mongodb = use_mongodb
        
        # PostgreSQL setup
        if use_postgres:
            self._setup_postgres()
        
        # MongoDB setup
        if use_mongodb:
            self._setup_mongodb()
    
    def _setup_postgres(self):
        """Setup PostgreSQL connection"""
        try:
            connection_string = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
            self.postgres_engine = create_engine(connection_string)
            self.PostgresSession = sessionmaker(bind=self.postgres_engine)
            
            # Create tables
            Base.metadata.create_all(self.postgres_engine)
            logger.info("PostgreSQL connection established and tables created")
        except Exception as e:
            logger.error(f"Error setting up PostgreSQL: {e}")
            self.use_postgres = False
    
    def _setup_mongodb(self):
        """Setup MongoDB connection"""
        try:
            self.mongo_client = MongoClient(MONGODB_URI)
            self.mongo_db = self.mongo_client[MONGODB_DB]
            self.blocks_collection = self.mongo_db['blocks']
            self.transactions_collection = self.mongo_db['transactions']
            
            # Create indexes
            self.blocks_collection.create_index("block_number")
            self.transactions_collection.create_index("tx_hash")
            self.transactions_collection.create_index("block_number")
            
            logger.info("MongoDB connection established and indexes created")
        except Exception as e:
            logger.error(f"Error setting up MongoDB: {e}")
            self.use_mongodb = False
    
    def store_block(self, block_data: Dict[str, Any]) -> bool:
        """
        Store block data in databases
        
        Args:
            block_data: Block data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        success = True
        
        # Store in PostgreSQL
        if self.use_postgres:
            try:
                session = self.PostgresSession()
                
                # Create block record
                block_record = Block(
                    block_number=block_data['block_number'],
                    block_hash=block_data['block_hash'],
                    parent_hash=block_data['parent_hash'],
                    timestamp=block_data['timestamp'],
                    miner=block_data['miner'],
                    difficulty=block_data['difficulty'],
                    gas_limit=block_data['gas_limit'],
                    gas_used=block_data['gas_used'],
                    transaction_count=block_data['transaction_count']
                )
                
                session.add(block_record)
                session.commit()
                session.close()
                logger.info(f"Stored block {block_data['block_number']} in PostgreSQL")
            except Exception as e:
                logger.error(f"Error storing block in PostgreSQL: {e}")
                success = False
        
        # Store in MongoDB
        if self.use_mongodb:
            try:
                # Add timestamp for MongoDB
                block_data['created_at'] = datetime.utcnow()
                self.blocks_collection.insert_one(block_data)
                logger.info(f"Stored block {block_data['block_number']} in MongoDB")
            except Exception as e:
                logger.error(f"Error storing block in MongoDB: {e}")
                success = False
        
        return success
    
    def store_transaction(self, tx_data: Dict[str, Any]) -> bool:
        """
        Store transaction data in databases
        
        Args:
            tx_data: Transaction data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        success = True
        
        # Store in PostgreSQL
        if self.use_postgres:
            try:
                session = self.PostgresSession()
                
                # Create transaction record
                tx_record = Transaction(
                    tx_hash=tx_data['tx_hash'],
                    block_number=tx_data['block_number'],
                    from_address=tx_data['from_address'],
                    to_address=tx_data['to_address'],
                    value_wei=tx_data['value_wei'],
                    value_ether=float(tx_data['value_ether']),
                    gas=tx_data['gas'],
                    gas_price=tx_data['gas_price'],
                    gas_price_gwei=float(tx_data['gas_price_gwei']),
                    input_data=tx_data['input_data'],
                    nonce=tx_data['nonce'],
                    transaction_index=tx_data['transaction_index']
                )
                
                session.add(tx_record)
                session.commit()
                session.close()
                logger.info(f"Stored transaction {tx_data['tx_hash'][:20]}... in PostgreSQL")
            except Exception as e:
                logger.error(f"Error storing transaction in PostgreSQL: {e}")
                success = False
        
        # Store in MongoDB
        if self.use_mongodb:
            try:
                # Add timestamp for MongoDB
                tx_data['created_at'] = datetime.utcnow()
                self.transactions_collection.insert_one(tx_data)
                logger.info(f"Stored transaction {tx_data['tx_hash'][:20]}... in MongoDB")
            except Exception as e:
                logger.error(f"Error storing transaction in MongoDB: {e}")
                success = False
        
        return success
    
    def store_block_with_transactions(self, block_data: Dict[str, Any]) -> bool:
        """
        Store block and all its transactions
        
        Args:
            block_data: Block data with transactions
            
        Returns:
            True if successful, False otherwise
        """
        # Store block
        block_success = self.store_block(block_data)
        
        # Store transactions
        transactions_success = True
        for tx in block_data.get('transactions', []):
            if not self.store_transaction(tx):
                transactions_success = False
        
        return block_success and transactions_success
    
    def get_block(self, block_number: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve block data from database
        
        Args:
            block_number: Block number to retrieve
            
        Returns:
            Block data or None if not found
        """
        # Try PostgreSQL first
        if self.use_postgres:
            try:
                session = self.PostgresSession()
                block = session.query(Block).filter(Block.block_number == block_number).first()
                session.close()
                
                if block:
                    return {
                        'block_number': block.block_number,
                        'block_hash': block.block_hash,
                        'parent_hash': block.parent_hash,
                        'timestamp': block.timestamp,
                        'miner': block.miner,
                        'difficulty': block.difficulty,
                        'gas_limit': block.gas_limit,
                        'gas_used': block.gas_used,
                        'transaction_count': block.transaction_count
                    }
            except Exception as e:
                logger.error(f"Error retrieving block from PostgreSQL: {e}")
        
        # Try MongoDB
        if self.use_mongodb:
            try:
                block = self.blocks_collection.find_one({'block_number': block_number})
                if block:
                    # Remove MongoDB-specific fields
                    block.pop('_id', None)
                    return block
            except Exception as e:
                logger.error(f"Error retrieving block from MongoDB: {e}")
        
        return None
    
    def get_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve transaction data from database
        
        Args:
            tx_hash: Transaction hash to retrieve
            
        Returns:
            Transaction data or None if not found
        """
        # Try PostgreSQL first
        if self.use_postgres:
            try:
                session = self.PostgresSession()
                tx = session.query(Transaction).filter(Transaction.tx_hash == tx_hash).first()
                session.close()
                
                if tx:
                    return {
                        'tx_hash': tx.tx_hash,
                        'block_number': tx.block_number,
                        'from_address': tx.from_address,
                        'to_address': tx.to_address,
                        'value_wei': tx.value_wei,
                        'value_ether': tx.value_ether,
                        'gas': tx.gas,
                        'gas_price': tx.gas_price,
                        'gas_price_gwei': tx.gas_price_gwei,
                        'input_data': tx.input_data,
                        'nonce': tx.nonce,
                        'transaction_index': tx.transaction_index
                    }
            except Exception as e:
                logger.error(f"Error retrieving transaction from PostgreSQL: {e}")
        
        # Try MongoDB
        if self.use_mongodb:
            try:
                tx = self.transactions_collection.find_one({'tx_hash': tx_hash})
                if tx:
                    # Remove MongoDB-specific fields
                    tx.pop('_id', None)
                    return tx
            except Exception as e:
                logger.error(f"Error retrieving transaction from MongoDB: {e}")
        
        return None
    
    def get_blocks_in_range(self, start_block: int, end_block: int) -> List[Dict[str, Any]]:
        """
        Retrieve blocks in a range
        
        Args:
            start_block: Starting block number
            end_block: Ending block number
            
        Returns:
            List of block data
        """
        blocks = []
        
        # Try PostgreSQL first
        if self.use_postgres:
            try:
                session = self.PostgresSession()
                db_blocks = session.query(Block).filter(
                    Block.block_number >= start_block,
                    Block.block_number <= end_block
                ).all()
                session.close()
                
                for block in db_blocks:
                    blocks.append({
                        'block_number': block.block_number,
                        'block_hash': block.block_hash,
                        'parent_hash': block.parent_hash,
                        'timestamp': block.timestamp,
                        'miner': block.miner,
                        'difficulty': block.difficulty,
                        'gas_limit': block.gas_limit,
                        'gas_used': block.gas_used,
                        'transaction_count': block.transaction_count
                    })
            except Exception as e:
                logger.error(f"Error retrieving blocks from PostgreSQL: {e}")
        
        # Try MongoDB if PostgreSQL failed or returned no results
        if not blocks and self.use_mongodb:
            try:
                cursor = self.blocks_collection.find({
                    'block_number': {'$gte': start_block, '$lte': end_block}
                }).sort('block_number', 1)
                
                for block in cursor:
                    block.pop('_id', None)
                    blocks.append(block)
            except Exception as e:
                logger.error(f"Error retrieving blocks from MongoDB: {e}")
        
        return blocks
    
    def close(self):
        """Close database connections"""
        if hasattr(self, 'postgres_engine'):
            self.postgres_engine.dispose()
        if hasattr(self, 'mongo_client'):
            self.mongo_client.close()
        logger.info("Database connections closed")


# Example usage
if __name__ == "__main__":
    # Test database connection
    db_manager = DatabaseManager(use_postgres=False, use_mongodb=True)  # Use only MongoDB for testing
    
    # Test storing and retrieving data
    test_block = {
        'block_number': 999999,
        'block_hash': '0x' + 'a' * 64,
        'parent_hash': '0x' + 'b' * 64,
        'timestamp': 1234567890,
        'miner': '0x' + 'c' * 40,
        'difficulty': 1000000,
        'gas_limit': 15000000,
        'gas_used': 1000000,
        'transaction_count': 5
    }
    
    # Store test block
    success = db_manager.store_block(test_block)
    print(f"Stored test block: {success}")
    
    # Retrieve test block
    retrieved_block = db_manager.get_block(999999)
    print(f"Retrieved block: {retrieved_block is not None}")
    
    db_manager.close() 