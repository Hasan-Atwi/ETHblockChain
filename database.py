"""
Database Module
Handles database connections and operations for storing blockchain data

This module provides a unified interface for storing and retrieving Ethereum blockchain data
in both PostgreSQL (relational database) and MongoDB (document database). It handles:

1. Database connections and setup
2. Data models for blocks and transactions
3. CRUD operations (Create, Read, Update, Delete)
4. Error handling and logging
5. Connection management and cleanup

The module supports dual database storage, allowing data to be stored in both
PostgreSQL and MongoDB simultaneously for redundancy and different query capabilities.
"""

import logging
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, BigInteger, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from datetime import datetime
import json
from config import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD,
    MONGODB_URI, MONGODB_DB
)

# Set up logging configuration for database operations
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy setup - creates the base class for all database models
Base = declarative_base()


class Block(Base):
    """
    PostgreSQL database model for Ethereum blocks
    
    This class defines the structure of the 'blocks' table in PostgreSQL.
    Each field corresponds to a specific piece of data from an Ethereum block.
    
    Fields:
    - block_number: Unique identifier for the block (primary key)
    - block_hash: Hash of the block (unique identifier)
    - parent_hash: Hash of the previous block (for chain linking)
    - timestamp: Unix timestamp when block was mined
    - miner: Address of the miner who created the block
    - difficulty: Mining difficulty at the time
    - gas_limit: Maximum gas allowed in the block
    - gas_used: Actual gas used in the block
    - transaction_count: Number of transactions in the block
    - created_at: When this record was created in our database
    """
    __tablename__ = 'blocks'  # Name of the table in PostgreSQL
    
    # Primary key - block number is unique and identifies each block
    block_number = Column(BigInteger, primary_key=True)
    
    # Block hash - unique identifier for the block (66 chars: 0x + 64 hex chars)
    block_hash = Column(String(66), unique=True, nullable=False)
    
    # Parent block hash - links to previous block in the chain
    parent_hash = Column(String(66), nullable=False)
    
    # Unix timestamp when the block was mined
    timestamp = Column(BigInteger, nullable=False)
    
    # Ethereum address of the miner (42 chars: 0x + 40 hex chars)
    miner = Column(String(42), nullable=False)
    
    # Mining difficulty - how hard it was to mine this block
    difficulty = Column(BigInteger, nullable=False)
    
    # Gas limit - maximum gas allowed in this block
    gas_limit = Column(BigInteger, nullable=False)
    
    # Gas used - actual gas consumed by transactions in this block
    gas_used = Column(BigInteger, nullable=False)
    
    # Number of transactions contained in this block
    transaction_count = Column(Integer, nullable=False)
    
    # Timestamp when this record was created in our database
    created_at = Column(DateTime, default=datetime.utcnow)


class Transaction(Base):
    """
    PostgreSQL database model for Ethereum transactions
    
    This class defines the structure of the 'transactions' table in PostgreSQL.
    Each field corresponds to a specific piece of data from an Ethereum transaction.
    
    Fields:
    - tx_hash: Unique identifier for the transaction (primary key)
    - block_number: Which block this transaction belongs to
    - from_address: Sender's Ethereum address
    - to_address: Recipient's Ethereum address (can be null for contract creation)
    - value_wei: Transaction value in Wei (smallest unit)
    - value_ether: Transaction value in Ether (human-readable)
    - gas: Gas limit for this transaction
    - gas_price: Price per unit of gas in Wei
    - gas_price_gwei: Price per unit of gas in Gwei (human-readable)
    - input_data: Additional data sent with the transaction
    - nonce: Transaction nonce (prevents replay attacks)
    - transaction_index: Position of transaction within the block
    - created_at: When this record was created in our database
    """
    __tablename__ = 'transactions'  # Name of the table in PostgreSQL
    
    # Primary key - transaction hash is unique and identifies each transaction
    tx_hash = Column(String(66), primary_key=True)
    
    # Foreign key reference to the block this transaction belongs to
    block_number = Column(BigInteger, nullable=False)
    
    # Sender's Ethereum address (42 chars: 0x + 40 hex chars)
    from_address = Column(String(42), nullable=False)
    
    # Recipient's Ethereum address (can be null for contract creation)
    to_address = Column(String(42), nullable=True)
    
    # Transaction value in Wei (smallest unit of Ether)
    value_wei = Column(Numeric(78, 0), nullable=False)  # NUMERIC can handle very large numbers
    
    # Transaction value in Ether (human-readable format)
    value_ether = Column(Float, nullable=False)
    
    # Gas limit for this transaction
    gas = Column(BigInteger, nullable=False)
    
    # Gas price in Wei
    gas_price = Column(Numeric(78, 0), nullable=False)  # NUMERIC can handle very large numbers
    
    # Gas price in Gwei (human-readable format)
    gas_price_gwei = Column(Float, nullable=False)
    
    # Additional data sent with the transaction (can be null)
    input_data = Column(Text, nullable=True)
    
    # Transaction nonce (prevents replay attacks)
    nonce = Column(BigInteger, nullable=False)
    
    # Position of this transaction within the block
    transaction_index = Column(Integer, nullable=False)
    
    # Timestamp when this record was created in our database
    created_at = Column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    """
    Main database management class
    
    This class provides a unified interface for storing and retrieving blockchain data
    from both PostgreSQL and MongoDB databases. It handles:
    
    1. Database connections and setup
    2. Data storage operations (blocks and transactions)
    3. Data retrieval operations
    4. Error handling and logging
    5. Connection cleanup
    
    The class supports dual database storage, allowing data to be stored in both
    databases simultaneously for redundancy and different query capabilities.
    """
    
    def __init__(self, use_postgres: bool = True, use_mongodb: bool = True):
        """
        Initialize the database manager
        
        This method sets up connections to the specified databases and creates
        necessary tables/indexes for storing blockchain data.
        
        Args:
            use_postgres: Whether to use PostgreSQL database
            use_mongodb: Whether to use MongoDB database
            
        Note: Both databases can be used simultaneously for redundancy
        """
        # Store database preferences
        self.use_postgres = use_postgres
        self.use_mongodb = use_mongodb
        
        # Initialize PostgreSQL connection if requested
        if use_postgres:
            self._setup_postgres()
        
        # Initialize MongoDB connection if requested
        if use_mongodb:
            self._setup_mongodb()
    
    def _setup_postgres(self):
        """
        Set up PostgreSQL database connection and create tables
        
        This method:
        1. Creates a connection to PostgreSQL using SQLAlchemy
        2. Tests the connection to ensure it's working
        3. Creates the database tables if they don't exist
        4. Sets up the session factory for database operations
        
        Raises:
            Exception: If connection fails or setup fails
        """
        try:
            # Create connection string for PostgreSQL
            # Format: postgresql://username:password@host:port/database
            connection_string = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
            
            logger.info(f"Attempting to connect to PostgreSQL with: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
            
            # Create SQLAlchemy engine for database connection
            self.postgres_engine = create_engine(connection_string)
            
            # Test the connection by executing a simple query
            with self.postgres_engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("SELECT 1")).fetchone()
            
            # Create session factory for database operations
            # This allows us to create database sessions for transactions
            self.PostgresSession = sessionmaker(bind=self.postgres_engine)
            
            # Drop and recreate tables to handle schema changes
            Base.metadata.drop_all(self.postgres_engine)
            Base.metadata.create_all(self.postgres_engine)
            
            logger.info("PostgreSQL connection established and tables created")
            
        except Exception as e:
            logger.error(f"Error setting up PostgreSQL: {e}")
            self.use_postgres = False
            # Re-raise the exception so the calling code knows about the failure
            raise
    
    def _setup_mongodb(self):
        """
        Set up MongoDB database connection and create indexes
        
        This method:
        1. Creates a connection to MongoDB using PyMongo
        2. Tests the connection to ensure it's working
        3. Sets up collections for blocks and transactions
        4. Creates indexes for efficient querying
        
        Raises:
            Exception: If connection fails or setup fails
        """
        try:
            # Create MongoDB client with connection timeout
            # serverSelectionTimeoutMS=5000 means it will timeout after 5 seconds
            self.mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            
            # Test the connection by pinging the admin database
            self.mongo_client.admin.command('ping')
            
            # Get reference to our database
            self.mongo_db = self.mongo_client[MONGODB_DB]
            
            # Get references to our collections (similar to tables in SQL)
            self.blocks_collection = self.mongo_db['blocks']
            self.transactions_collection = self.mongo_db['transactions']
            
            # Create indexes for efficient querying
            # Indexes speed up queries on these fields
            self.blocks_collection.create_index("block_number")  # For finding blocks by number
            self.transactions_collection.create_index("tx_hash")  # For finding transactions by hash
            self.transactions_collection.create_index("block_number")  # For finding transactions by block
            
            logger.info("MongoDB connection established and indexes created")
            
        except Exception as e:
            logger.error(f"Error setting up MongoDB: {e}")
            self.use_mongodb = False
            # Re-raise the exception so the calling code knows about the failure
            raise
    
    def store_block(self, block_data: Dict[str, Any]) -> bool:
        """
        Store block data in the configured databases
        
        This method stores a single block's data in both PostgreSQL and MongoDB
        (if both are configured). It handles the different data formats required
        by each database type.
        
        Args:
            block_data: Dictionary containing block information with keys:
                - block_number: Block number
                - block_hash: Block hash
                - parent_hash: Parent block hash
                - timestamp: Block timestamp
                - miner: Miner address
                - difficulty: Mining difficulty
                - gas_limit: Gas limit
                - gas_used: Gas used
                - transaction_count: Number of transactions
                
        Returns:
            bool: True if storage was successful in at least one database, False otherwise
            
        Note: The method attempts to store in both databases and returns True
        if at least one succeeds, providing redundancy.
        """
        success = True
        
        # ===== STORE IN POSTGRESQL =====
        if self.use_postgres:
            try:
                # Create a new database session
                session = self.PostgresSession()
                
                # Create a Block record object from the data
                # This maps the dictionary data to our SQLAlchemy model
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
                
                # Add the record to the session and commit to database
                session.add(block_record)
                session.commit()
                session.close()
                
                logger.info(f"Stored block {block_data['block_number']} in PostgreSQL")
                
            except Exception as e:
                logger.error(f"Error storing block in PostgreSQL: {e}")
                success = False
        
        # ===== STORE IN MONGODB =====
        if self.use_mongodb:
            try:
                # Add timestamp for MongoDB (MongoDB doesn't have automatic timestamps)
                block_data['created_at'] = datetime.utcnow()
                
                # Insert the block data directly into MongoDB collection
                # MongoDB stores data as JSON-like documents
                self.blocks_collection.insert_one(block_data)
                
                logger.info(f"Stored block {block_data['block_number']} in MongoDB")
                
            except Exception as e:
                logger.error(f"Error storing block in MongoDB: {e}")
                success = False
        
        return success
    
    def store_transaction(self, tx_data: Dict[str, Any]) -> bool:
        """
        Store transaction data in the configured databases
        
        This method stores a single transaction's data in both PostgreSQL and MongoDB
        (if both are configured). It handles the different data formats required
        by each database type.
        
        Args:
            tx_data: Dictionary containing transaction information with keys:
                - tx_hash: Transaction hash
                - block_number: Block number containing this transaction
                - from_address: Sender address
                - to_address: Recipient address
                - value_wei: Transaction value in Wei
                - value_ether: Transaction value in Ether
                - gas: Gas limit
                - gas_price: Gas price in Wei
                - gas_price_gwei: Gas price in Gwei
                - input_data: Transaction input data
                - nonce: Transaction nonce
                - transaction_index: Position in block
                
        Returns:
            bool: True if storage was successful in at least one database, False otherwise
        """
        success = True
        
        # ===== STORE IN POSTGRESQL =====
        if self.use_postgres:
            try:
                # Create a new database session
                session = self.PostgresSession()
                
                # Create a Transaction record object from the data
                # Convert numeric values to appropriate types
                tx_record = Transaction(
                    tx_hash=tx_data['tx_hash'],
                    block_number=tx_data['block_number'],
                    from_address=tx_data['from_address'],
                    to_address=tx_data['to_address'],
                    value_wei=str(tx_data['value_wei']),  # Convert to string for NUMERIC
                    value_ether=float(tx_data['value_ether']),  # Convert to float for storage
                    gas=tx_data['gas'],
                    gas_price=str(tx_data['gas_price']),  # Convert to string for NUMERIC
                    gas_price_gwei=float(tx_data['gas_price_gwei']),  # Convert to float
                    input_data=tx_data['input_data'],
                    nonce=tx_data['nonce'],
                    transaction_index=tx_data['transaction_index']
                )
                
                # Add the record to the session and commit to database
                session.add(tx_record)
                session.commit()
                session.close()
                
                logger.info(f"Stored transaction {tx_data['tx_hash'][:20]}... in PostgreSQL")
                
            except Exception as e:
                logger.error(f"Error storing transaction in PostgreSQL: {e}")
                success = False
        
        # ===== STORE IN MONGODB =====
        if self.use_mongodb:
            try:
                # Add timestamp for MongoDB
                tx_data['created_at'] = datetime.utcnow()
                
                # Insert the transaction data directly into MongoDB collection
                self.transactions_collection.insert_one(tx_data)
                
                logger.info(f"Stored transaction {tx_data['tx_hash'][:20]}... in MongoDB")
                
            except Exception as e:
                logger.error(f"Error storing transaction in MongoDB: {e}")
                success = False
        
        return success
    
    def store_block_with_transactions(self, block_data: Dict[str, Any]) -> bool:
        """
        Store a block and all its transactions
        
        This method stores a complete block with all its transactions. It first
        stores the block data, then stores each transaction individually. This
        ensures that both block and transaction data are properly stored.
        
        Args:
            block_data: Dictionary containing block information plus a 'transactions'
                       list containing transaction dictionaries
                
        Returns:
            bool: True if both block and all transactions were stored successfully
            
        Note: This method requires the block_data to contain a 'transactions' list
        with transaction dictionaries.
        """
        # First, store the block data (without transactions)
        block_success = self.store_block(block_data)
        
        # Then, store each transaction in the block
        transactions_success = True
        for tx in block_data.get('transactions', []):
            if not self.store_transaction(tx):
                transactions_success = False
        
        # Return True only if both block and all transactions were stored successfully
        return block_success and transactions_success
    
    def get_block(self, block_number: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve block data from database
        
        This method attempts to retrieve block data from PostgreSQL first, then
        MongoDB if PostgreSQL fails or returns no results. This provides redundancy
        and allows the system to work even if one database is unavailable.
        
        Args:
            block_number: The block number to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Block data dictionary or None if not found
            
        Note: The returned data structure matches the input format used by store_block()
        """
        # ===== TRY POSTGRESQL FIRST =====
        if self.use_postgres:
            try:
                # Create a new database session
                session = self.PostgresSession()
                
                # Query for the block with the specified block number
                block = session.query(Block).filter(Block.block_number == block_number).first()
                session.close()
                
                # If block found, convert SQLAlchemy object to dictionary
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
        
        # ===== TRY MONGODB IF POSTGRESQL FAILED =====
        if self.use_mongodb:
            try:
                # Query MongoDB for the block
                block = self.blocks_collection.find_one({'block_number': block_number})
                
                if block:
                    # Remove MongoDB-specific fields (_id) before returning
                    block.pop('_id', None)
                    return block
                    
            except Exception as e:
                logger.error(f"Error retrieving block from MongoDB: {e}")
        
        # Return None if block not found in either database
        return None
    
    def get_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve transaction data from database
        
        This method attempts to retrieve transaction data from PostgreSQL first, then
        MongoDB if PostgreSQL fails or returns no results. This provides redundancy
        and allows the system to work even if one database is unavailable.
        
        Args:
            tx_hash: The transaction hash to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Transaction data dictionary or None if not found
            
        Note: The returned data structure matches the input format used by store_transaction()
        """
        # ===== TRY POSTGRESQL FIRST =====
        if self.use_postgres:
            try:
                # Create a new database session
                session = self.PostgresSession()
                
                # Query for the transaction with the specified hash
                tx = session.query(Transaction).filter(Transaction.tx_hash == tx_hash).first()
                session.close()
                
                # If transaction found, convert SQLAlchemy object to dictionary
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
        
        # ===== TRY MONGODB IF POSTGRESQL FAILED =====
        if self.use_mongodb:
            try:
                # Query MongoDB for the transaction
                tx = self.transactions_collection.find_one({'tx_hash': tx_hash})
                
                if tx:
                    # Remove MongoDB-specific fields (_id) before returning
                    tx.pop('_id', None)
                    return tx
                    
            except Exception as e:
                logger.error(f"Error retrieving transaction from MongoDB: {e}")
        
        # Return None if transaction not found in either database
        return None
    
    def get_blocks_in_range(self, start_block: int, end_block: int) -> List[Dict[str, Any]]:
        """
        Retrieve multiple blocks within a specified range
        
        This method retrieves all blocks between start_block and end_block (inclusive).
        It tries PostgreSQL first, then MongoDB if PostgreSQL fails or returns no results.
        This is useful for retrieving historical data or analyzing block ranges.
        
        Args:
            start_block: Starting block number (inclusive)
            end_block: Ending block number (inclusive)
            
        Returns:
            List[Dict[str, Any]]: List of block data dictionaries
            
        Note: Blocks are returned in ascending order by block number
        """
        blocks = []
        
        # ===== TRY POSTGRESQL FIRST =====
        if self.use_postgres:
            try:
                # Create a new database session
                session = self.PostgresSession()
                
                # Query for blocks in the specified range
                db_blocks = session.query(Block).filter(
                    Block.block_number >= start_block,
                    Block.block_number <= end_block
                ).all()
                session.close()
                
                # Convert SQLAlchemy objects to dictionaries
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
        
        # ===== TRY MONGODB IF POSTGRESQL FAILED OR RETURNED NO RESULTS =====
        if not blocks and self.use_mongodb:
            try:
                # Query MongoDB for blocks in the specified range
                # $gte = greater than or equal, $lte = less than or equal
                cursor = self.blocks_collection.find({
                    'block_number': {'$gte': start_block, '$lte': end_block}
                }).sort('block_number', 1)  # Sort by block number ascending
                
                # Convert MongoDB documents to dictionaries
                for block in cursor:
                    block.pop('_id', None)  # Remove MongoDB-specific field
                    blocks.append(block)
                    
            except Exception as e:
                logger.error(f"Error retrieving blocks from MongoDB: {e}")
        
        return blocks
    
    def get_total_blocks_count(self) -> int:
        """
        Get total number of blocks in the database
        
        Returns:
            int: Total number of blocks stored
        """
        if self.use_postgres:
            try:
                session = self.PostgresSession()
                count = session.query(Block).count()
                session.close()
                return count
            except Exception as e:
                logger.error(f"Error getting block count from PostgreSQL: {e}")
                return 0
        
        if self.use_mongodb:
            try:
                return self.blocks_collection.count_documents({})
            except Exception as e:
                logger.error(f"Error getting block count from MongoDB: {e}")
                return 0
        
        return 0
    
    def get_total_transactions_count(self) -> int:
        """
        Get total number of transactions in the database
        
        Returns:
            int: Total number of transactions stored
        """
        if self.use_postgres:
            try:
                session = self.PostgresSession()
                count = session.query(Transaction).count()
                session.close()
                return count
            except Exception as e:
                logger.error(f"Error getting transaction count from PostgreSQL: {e}")
                return 0
        
        if self.use_mongodb:
            try:
                return self.transactions_collection.count_documents({})
            except Exception as e:
                logger.error(f"Error getting transaction count from MongoDB: {e}")
                return 0
        
        return 0
    
    def get_latest_block_from_db(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest block from the database
        
        Returns:
            Optional[Dict[str, Any]]: Latest block data or None if no blocks exist
        """
        if self.use_postgres:
            try:
                session = self.PostgresSession()
                block = session.query(Block).order_by(Block.block_number.desc()).first()
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
                logger.error(f"Error getting latest block from PostgreSQL: {e}")
        
        if self.use_mongodb:
            try:
                block = self.blocks_collection.find_one(
                    sort=[('block_number', -1)]
                )
                if block:
                    block.pop('_id', None)
                    return block
            except Exception as e:
                logger.error(f"Error getting latest block from MongoDB: {e}")
        
        return None
    
    def get_recent_blocks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent blocks from the database
        
        Args:
            limit: Maximum number of blocks to return
            
        Returns:
            List[Dict[str, Any]]: List of recent block data
        """
        if self.use_postgres:
            try:
                session = self.PostgresSession()
                blocks = session.query(Block).order_by(Block.block_number.desc()).limit(limit).all()
                session.close()
                
                return [{
                    'block_number': block.block_number,
                    'block_hash': block.block_hash,
                    'parent_hash': block.parent_hash,
                    'timestamp': block.timestamp,
                    'miner': block.miner,
                    'difficulty': block.difficulty,
                    'gas_limit': block.gas_limit,
                    'gas_used': block.gas_used,
                    'transaction_count': block.transaction_count
                } for block in blocks]
            except Exception as e:
                logger.error(f"Error getting recent blocks from PostgreSQL: {e}")
                return []
        
        if self.use_mongodb:
            try:
                blocks = list(self.blocks_collection.find(
                    sort=[('block_number', -1)]
                ).limit(limit))
                
                # Remove MongoDB-specific fields
                for block in blocks:
                    block.pop('_id', None)
                
                return blocks
            except Exception as e:
                logger.error(f"Error getting recent blocks from MongoDB: {e}")
                return []
        
        return []
    
    def get_recent_transactions(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Get recent transactions from the database
        
        Args:
            limit: Maximum number of transactions to return
            
        Returns:
            List[Dict[str, Any]]: List of recent transaction data
        """
        if self.use_postgres:
            try:
                session = self.PostgresSession()
                transactions = session.query(Transaction).order_by(Transaction.block_number.desc()).limit(limit).all()
                session.close()
                
                return [{
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
                } for tx in transactions]
            except Exception as e:
                logger.error(f"Error getting recent transactions from PostgreSQL: {e}")
                return []
        
        if self.use_mongodb:
            try:
                transactions = list(self.transactions_collection.find(
                    sort=[('block_number', -1)]
                ).limit(limit))
                
                # Remove MongoDB-specific fields
                for tx in transactions:
                    tx.pop('_id', None)
                
                return transactions
            except Exception as e:
                logger.error(f"Error getting recent transactions from MongoDB: {e}")
                return []
        
        return []
    
    def get_all_blocks(self) -> List[Dict[str, Any]]:
        """
        Get all blocks from the database
        
        Returns:
            List[Dict[str, Any]]: List of all block data
        """
        if self.use_postgres:
            try:
                session = self.PostgresSession()
                blocks = session.query(Block).order_by(Block.block_number.asc()).all()
                session.close()
                
                return [{
                    'block_number': block.block_number,
                    'block_hash': block.block_hash,
                    'parent_hash': block.parent_hash,
                    'timestamp': block.timestamp,
                    'miner': block.miner,
                    'difficulty': block.difficulty,
                    'gas_limit': block.gas_limit,
                    'gas_used': block.gas_used,
                    'transaction_count': block.transaction_count
                } for block in blocks]
            except Exception as e:
                logger.error(f"Error getting all blocks from PostgreSQL: {e}")
                return []
        
        if self.use_mongodb:
            try:
                blocks = list(self.blocks_collection.find().sort('block_number', 1))
                
                # Remove MongoDB-specific fields
                for block in blocks:
                    block.pop('_id', None)
                
                return blocks
            except Exception as e:
                logger.error(f"Error getting all blocks from MongoDB: {e}")
                return []
        
        return []
    
    def close(self):
        """
        Close all database connections and clean up resources
        
        This method properly closes all database connections to prevent
        resource leaks and ensure clean shutdown of the application.
        """
        # Close PostgreSQL engine (this closes all connections in the pool)
        if hasattr(self, 'postgres_engine'):
            self.postgres_engine.dispose()
            
        # Close MongoDB client connection
        if hasattr(self, 'mongo_client'):
            self.mongo_client.close()
            
        logger.info("Database connections closed")


# ===== EXAMPLE USAGE AND TESTING =====
if __name__ == "__main__":
    """
    Example usage and testing of the DatabaseManager class
    
    This section demonstrates how to use the DatabaseManager to store and
    retrieve blockchain data. It's useful for testing the database functionality.
    """
    # Test database connection (use only MongoDB for testing to avoid PostgreSQL dependency)
    db_manager = DatabaseManager(use_postgres=False, use_mongodb=True)
    
    # Create test block data
    test_block = {
        'block_number': 999999,
        'block_hash': '0x' + 'a' * 64,  # 64-character hex string
        'parent_hash': '0x' + 'b' * 64,  # 64-character hex string
        'timestamp': 1234567890,  # Unix timestamp
        'miner': '0x' + 'c' * 40,  # 40-character Ethereum address
        'difficulty': 1000000,
        'gas_limit': 15000000,
        'gas_used': 1000000,
        'transaction_count': 5
    }
    
    # Store test block in database
    success = db_manager.store_block(test_block)
    print(f"Stored test block: {success}")
    
    # Retrieve test block from database
    retrieved_block = db_manager.get_block(999999)
    print(f"Retrieved block: {retrieved_block is not None}")
    
    # Clean up database connections
    db_manager.close() 