"""
Main Script for Blockchain Data Collector
Command-line interface for running the ETL pipeline

This script provides a command-line interface (CLI) for the Ethereum blockchain data collector.
It allows users to:
1. Collect blockchain data (latest blocks, historical blocks, or scheduled collection)
2. Run a Streamlit dashboard for data visualization
3. Test the blockchain connection and database functionality

The script uses argparse to handle different command-line arguments and subcommands.
"""

import argparse
import logging
import sys
from datetime import datetime
from etl_pipeline import ETLPipeline
from config import BATCH_SIZE, START_BLOCK, END_BLOCK

# Set up comprehensive logging configuration
# This creates a dual logging setup: one for file output and one for console output
logging.basicConfig(
    level=logging.INFO,  # Log level set to INFO to capture important events
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Detailed log format with timestamp
    handlers=[
        logging.FileHandler('blockchain_collector.log'),  # Save logs to file for debugging
        logging.StreamHandler()  # Also display logs in console for real-time monitoring
    ]
)
logger = logging.getLogger(__name__)  # Create logger instance for this module


def main():
    """
    Main function that sets up the command-line interface and handles user commands
    
    This function:
    1. Creates an argument parser with subcommands for different operations
    2. Defines all available command-line options and their descriptions
    3. Parses user input and routes to appropriate functions
    4. Handles errors gracefully with proper logging and exit codes
    """
    # Create the main argument parser with detailed description and examples
    parser = argparse.ArgumentParser(
        description="Ethereum Blockchain Data Collector - A comprehensive tool for collecting and analyzing Ethereum blockchain data",
        formatter_class=argparse.RawDescriptionHelpFormatter,  # Preserves formatting in help text
        epilog="""
Examples:
  # Collect latest 10 blocks from the Ethereum blockchain
  python main.py collect --latest 10

  # Collect historical blocks from block 1000 to 1100 (useful for backfilling data)
  python main.py collect --historical --start 1000 --end 1100

  # Run scheduled collection every 5 minutes (for continuous data monitoring)
  python main.py collect --scheduled --interval 5

  # Launch the Streamlit dashboard for data visualization
  python main.py dashboard

  # Test the blockchain connection and database functionality
  python main.py test
        """
    )
    
    # Create subparsers for different commands (collect, dashboard, test)
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # ===== COLLECT COMMAND =====
    # This command handles all data collection operations
    collect_parser = subparsers.add_parser('collect', help='Collect blockchain data from Ethereum network')
    
    # Define all possible arguments for the collect command
    collect_parser.add_argument('--latest', type=int, 
                               help='Number of latest blocks to collect (e.g., --latest 10)')
    collect_parser.add_argument('--historical', action='store_true', 
                               help='Collect historical blocks (requires --start and --end)')
    collect_parser.add_argument('--start', type=int, default=START_BLOCK, 
                               help='Starting block number for historical collection')
    collect_parser.add_argument('--end', type=int, default=END_BLOCK, 
                               help='Ending block number for historical collection')
    collect_parser.add_argument('--scheduled', action='store_true', 
                               help='Run continuous scheduled collection')
    collect_parser.add_argument('--interval', type=int, default=5, 
                               help='Collection interval in minutes for scheduled collection')
    collect_parser.add_argument('--postgres', action='store_true', 
                               help='Use PostgreSQL database for data storage')
    collect_parser.add_argument('--mongodb', action='store_true', 
                               help='Use MongoDB database for data storage')
    
    # ===== DASHBOARD COMMAND =====
    # This command launches the Streamlit dashboard
    dashboard_parser = subparsers.add_parser('dashboard', 
                                           help='Launch Streamlit dashboard for data visualization')
    
    # ===== TEST COMMAND =====
    # This command tests the blockchain connection and database functionality
    test_parser = subparsers.add_parser('test', 
                                       help='Test blockchain connection and database functionality')
    
    # Parse the command-line arguments
    args = parser.parse_args()
    
    # If no command is provided, show help and exit
    if not args.command:
        parser.print_help()
        return
    
    # Execute the appropriate function based on the command
    try:
        if args.command == 'collect':
            run_collection(args)  # Handle data collection
        elif args.command == 'dashboard':
            run_dashboard()       # Launch dashboard
        elif args.command == 'test':
            run_test()           # Run tests
    
    except KeyboardInterrupt:
        # Handle graceful shutdown when user presses Ctrl+C
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        # Handle any unexpected errors with proper logging
        logger.error(f"Error: {e}")
        sys.exit(1)


def run_collection(args):
    """
    Execute data collection based on the provided arguments
    
    This function:
    1. Determines which database to use (PostgreSQL or MongoDB)
    2. Initializes the ETL pipeline
    3. Routes to the appropriate collection method based on arguments
    4. Handles different collection types: latest, historical, or scheduled
    5. Ensures proper cleanup of resources
    
    Args:
        args: Parsed command-line arguments containing collection parameters
    """
    logger.info("Starting blockchain data collection")
    
    # Determine which database to use based on command-line arguments
    # Default behavior: use PostgreSQL if no database is specified
    use_postgres = args.postgres or (not args.mongodb and not args.postgres)  # Default to PostgreSQL
    use_mongodb = args.mongodb or (not args.postgres and not args.mongodb)    # Default to MongoDB
    
    logger.info(f"Using PostgreSQL: {use_postgres}, MongoDB: {use_mongodb}")
    
    # Initialize the ETL pipeline with the chosen database configuration
    # The ETL pipeline handles the entire Extract-Transform-Load process
    pipeline = ETLPipeline(use_postgres=use_postgres, use_mongodb=use_mongodb)
    
    try:
        # ===== LATEST BLOCKS COLLECTION =====
        if args.latest:
            logger.info(f"Collecting latest {args.latest} blocks")
            # Process the most recent blocks from the blockchain
            stats = pipeline.process_latest_blocks(args.latest)
            print_collection_stats(stats)
        
        # ===== HISTORICAL BLOCKS COLLECTION =====
        elif args.historical:
            start_block = args.start
            # If end block is 0 or negative, use the latest block number
            end_block = args.end if args.end > 0 else pipeline.blockchain_client.get_latest_block_number()
            
            logger.info(f"Collecting historical blocks from {start_block} to {end_block}")
            # Process a range of historical blocks (useful for backfilling data)
            stats = pipeline.process_historical_blocks(start_block, end_block)
            print_collection_stats(stats)
        
        # ===== SCHEDULED COLLECTION =====
        elif args.scheduled:
            logger.info(f"Starting scheduled collection every {args.interval} minutes")
            # Run continuous collection at specified intervals (for monitoring)
            pipeline.run_scheduled_collection(args.interval)
        
        # ===== DEFAULT COLLECTION =====
        else:
            logger.info("No collection type specified, collecting latest blocks")
            # Default behavior: collect the latest blocks using the batch size from config
            stats = pipeline.process_latest_blocks(BATCH_SIZE)
            print_collection_stats(stats)
    
    finally:
        # Always ensure proper cleanup of database connections
        pipeline.close()


def run_dashboard():
    """
    Launch the Streamlit dashboard for data visualization
    
    This function:
    1. Imports the subprocess module to run Streamlit
    2. Launches the dashboard on localhost:8501
    3. Handles errors if Streamlit is not installed
    4. Provides helpful error messages for troubleshooting
    """
    logger.info("Starting Streamlit dashboard")
    
    try:
        import subprocess
        import sys
        
        # Launch Streamlit dashboard using subprocess
        # This runs the dashboard.py file as a Streamlit application
        subprocess.run([
            sys.executable,  # Use the current Python interpreter
            "-m", "streamlit", "run", "dashboard.py",  # Run dashboard.py with Streamlit
            "--server.port", "8501",  # Set port to 8501
            "--server.address", "localhost"  # Only allow local access
        ])
    
    except ImportError:
        # Handle case where Streamlit is not installed
        logger.error("Streamlit not installed. Install with: pip install streamlit")
        sys.exit(1)
    except Exception as e:
        # Handle any other errors during dashboard launch
        logger.error(f"Error running dashboard: {e}")
        sys.exit(1)


def run_test():
    """
    Test the blockchain connection and database functionality
    
    This function performs comprehensive testing of:
    1. Blockchain connection and data retrieval
    2. Database connection and data storage
    3. End-to-end data flow from blockchain to database
    
    The tests help ensure the system is working correctly before running data collection.
    """
    logger.info("Testing blockchain connection and functionality")
    
    try:
        from blockchain_client import BlockchainClient
        from database import DatabaseManager
        
        # ===== TEST 1: BLOCKCHAIN CONNECTION =====
        print("🔗 Testing blockchain connection...")
        client = BlockchainClient()  # Initialize blockchain client
        latest_block = client.get_latest_block_number()  # Get current block number
        print(f"✅ Connected to Ethereum. Latest block: {latest_block:,}")
        
        # ===== TEST 2: BLOCK RETRIEVAL =====
        print("📦 Testing block retrieval...")
        recent_block = client.get_block(latest_block - 1)  # Get the previous block
        if recent_block:
            print(f"✅ Retrieved block {recent_block['block_number']} with {recent_block['transaction_count']} transactions")
        else:
            print("❌ Failed to retrieve block")
            return  # Exit if we can't get block data
        
        # ===== TEST 3: DATABASE CONNECTION =====
        print("🗄️ Testing database connection...")
        
        # Try PostgreSQL first (more reliable for testing)
        print("  📊 Testing PostgreSQL connection...")
        try:
            db_manager_postgres = DatabaseManager(use_postgres=True, use_mongodb=False)
            print("  ✅ PostgreSQL connection successful")
            postgres_available = True
        except Exception as e:
            print(f"  ❌ PostgreSQL connection failed: {e}")
            postgres_available = False
        
        # Try MongoDB
        print("  🍃 Testing MongoDB connection...")
        try:
            db_manager_mongo = DatabaseManager(use_postgres=False, use_mongodb=True)
            print("  ✅ MongoDB connection successful")
            mongo_available = True
        except Exception as e:
            print(f"  ❌ MongoDB connection failed: {e}")
            print("  💡 To use MongoDB, install and start MongoDB server")
            mongo_available = False
        
        if not postgres_available and not mongo_available:
            print("❌ No database connections available!")
            print("💡 Please install and configure either PostgreSQL or MongoDB")
            return
        
        # ===== TEST 4: DATA STORAGE AND RETRIEVAL =====
        print("💾 Testing data storage...")
        
        # Use whichever database is available
        if postgres_available:
            db_manager = db_manager_postgres
            db_name = "PostgreSQL"
        else:
            db_manager = db_manager_mongo
            db_name = "MongoDB"
        
        if recent_block:
            # Try to store the retrieved block in the database
            success = db_manager.store_block_with_transactions(recent_block)
            if success:
                print(f"✅ Data storage test successful in {db_name}")
                
                # Test retrieving the stored data
                retrieved_block = db_manager.get_block(recent_block['block_number'])
                if retrieved_block:
                    print(f"✅ Data retrieval test successful in {db_name}")
                else:
                    print(f"❌ Data retrieval test failed in {db_name}")
            else:
                print(f"❌ Data storage test failed in {db_name}")
        
        # Clean up database connection
        db_manager.close()
        print("✅ All tests completed successfully!")
    
    except Exception as e:
        # Handle any errors during testing
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")
        sys.exit(1)


def print_collection_stats(stats):
    """
    Display comprehensive collection statistics in a formatted table
    
    This function takes the statistics dictionary returned by the ETL pipeline
    and displays it in a user-friendly format with clear labels and formatting.
    
    Args:
        stats: Dictionary containing collection statistics from the ETL pipeline
    """
    print("\n" + "="*50)
    print("COLLECTION STATISTICS")
    print("="*50)
    
    # Display block range information (for historical collections)
    if 'start_block' in stats and 'end_block' in stats:
        print(f"Block Range: {stats['start_block']:,} - {stats['end_block']:,}")
    
    # Display extraction statistics
    if 'blocks_extracted' in stats:
        print(f"Blocks Extracted: {stats['blocks_extracted']:,}")
    
    # Display loading statistics
    if 'blocks_loaded' in stats:
        print(f"Blocks Loaded: {stats['blocks_loaded']:,}")
    
    # Display processing time
    if 'processing_time' in stats:
        print(f"Processing Time: {stats['processing_time']:.2f} seconds")
    
    # Display cumulative statistics (for batch processing)
    if 'total_blocks_extracted' in stats:
        print(f"Total Blocks Extracted: {stats['total_blocks_extracted']:,}")
        print(f"Total Blocks Loaded: {stats['total_blocks_loaded']:,}")
        print(f"Total Processing Time: {stats['total_processing_time']:.2f} seconds")
        print(f"Batches Processed: {stats['batches_processed']}")
    
    # Display success/failure status
    if 'success' in stats:
        status = "✅ SUCCESS" if stats['success'] else "❌ FAILED"
        print(f"Status: {status}")
    
    # Display error information if any
    if 'error' in stats:
        print(f"Error: {stats['error']}")
    
    print("="*50)


# Entry point: only run main() if this script is executed directly
if __name__ == "__main__":
    main() 