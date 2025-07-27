"""
Main Script for Blockchain Data Collector
Command-line interface for running the ETL pipeline
"""

import argparse
import logging
import sys
from datetime import datetime
from etl_pipeline import ETLPipeline
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


def main():
    """Main function for command-line interface"""
    parser = argparse.ArgumentParser(
        description="Ethereum Blockchain Data Collector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect latest 10 blocks
  python main.py collect --latest 10

  # Collect historical blocks from 1000 to 1100
  python main.py collect --historical --start 1000 --end 1100

  # Run scheduled collection every 5 minutes
  python main.py collect --scheduled --interval 5

  # Run dashboard
  python main.py dashboard
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Collect command
    collect_parser = subparsers.add_parser('collect', help='Collect blockchain data')
    collect_parser.add_argument('--latest', type=int, help='Number of latest blocks to collect')
    collect_parser.add_argument('--historical', action='store_true', help='Collect historical blocks')
    collect_parser.add_argument('--start', type=int, default=START_BLOCK, help='Starting block number')
    collect_parser.add_argument('--end', type=int, default=END_BLOCK, help='Ending block number')
    collect_parser.add_argument('--scheduled', action='store_true', help='Run scheduled collection')
    collect_parser.add_argument('--interval', type=int, default=5, help='Collection interval in minutes')
    collect_parser.add_argument('--postgres', action='store_true', help='Use PostgreSQL')
    collect_parser.add_argument('--mongodb', action='store_true', help='Use MongoDB')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Run Streamlit dashboard')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test blockchain connection')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'collect':
            run_collection(args)
        elif args.command == 'dashboard':
            run_dashboard()
        elif args.command == 'test':
            run_test()
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


def run_collection(args):
    """Run data collection based on arguments"""
    logger.info("Starting blockchain data collection")
    
    # Determine database usage
    use_postgres = args.postgres or (not args.mongodb and not args.postgres)  # Default to PostgreSQL
    use_mongodb = args.mongodb or (not args.postgres and not args.mongodb)    # Default to MongoDB
    
    logger.info(f"Using PostgreSQL: {use_postgres}, MongoDB: {use_mongodb}")
    
    # Initialize ETL pipeline
    pipeline = ETLPipeline(use_postgres=use_postgres, use_mongodb=use_mongodb)
    
    try:
        if args.latest:
            logger.info(f"Collecting latest {args.latest} blocks")
            stats = pipeline.process_latest_blocks(args.latest)
            print_collection_stats(stats)
        
        elif args.historical:
            start_block = args.start
            end_block = args.end if args.end > 0 else pipeline.blockchain_client.get_latest_block_number()
            
            logger.info(f"Collecting historical blocks from {start_block} to {end_block}")
            stats = pipeline.process_historical_blocks(start_block, end_block)
            print_collection_stats(stats)
        
        elif args.scheduled:
            logger.info(f"Starting scheduled collection every {args.interval} minutes")
            pipeline.run_scheduled_collection(args.interval)
        
        else:
            logger.info("No collection type specified, collecting latest blocks")
            stats = pipeline.process_latest_blocks(BATCH_SIZE)
            print_collection_stats(stats)
    
    finally:
        pipeline.close()


def run_dashboard():
    """Run Streamlit dashboard"""
    logger.info("Starting Streamlit dashboard")
    
    try:
        import subprocess
        import sys
        
        # Run streamlit dashboard
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    
    except ImportError:
        logger.error("Streamlit not installed. Install with: pip install streamlit")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error running dashboard: {e}")
        sys.exit(1)


def run_test():
    """Test blockchain connection and basic functionality"""
    logger.info("Testing blockchain connection and functionality")
    
    try:
        from blockchain_client import BlockchainClient
        from database import DatabaseManager
        
        # Test blockchain connection
        print("🔗 Testing blockchain connection...")
        client = BlockchainClient()
        latest_block = client.get_latest_block_number()
        print(f"✅ Connected to Ethereum. Latest block: {latest_block:,}")
        
        # Test getting a recent block
        print("📦 Testing block retrieval...")
        recent_block = client.get_block(latest_block - 1)
        if recent_block:
            print(f"✅ Retrieved block {recent_block['block_number']} with {recent_block['transaction_count']} transactions")
        else:
            print("❌ Failed to retrieve block")
        
        # Test database connection
        print("🗄️ Testing database connection...")
        db_manager = DatabaseManager(use_postgres=False, use_mongodb=True)
        print("✅ Database connection established")
        
        # Test storing and retrieving data
        print("💾 Testing data storage...")
        if recent_block:
            success = db_manager.store_block_with_transactions(recent_block)
            if success:
                print("✅ Data storage test successful")
                
                # Test retrieval
                retrieved_block = db_manager.get_block(recent_block['block_number'])
                if retrieved_block:
                    print("✅ Data retrieval test successful")
                else:
                    print("❌ Data retrieval test failed")
            else:
                print("❌ Data storage test failed")
        
        db_manager.close()
        print("✅ All tests completed successfully!")
    
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")
        sys.exit(1)


def print_collection_stats(stats):
    """Print collection statistics"""
    print("\n" + "="*50)
    print("COLLECTION STATISTICS")
    print("="*50)
    
    if 'start_block' in stats and 'end_block' in stats:
        print(f"Block Range: {stats['start_block']:,} - {stats['end_block']:,}")
    
    if 'blocks_extracted' in stats:
        print(f"Blocks Extracted: {stats['blocks_extracted']:,}")
    
    if 'blocks_loaded' in stats:
        print(f"Blocks Loaded: {stats['blocks_loaded']:,}")
    
    if 'processing_time' in stats:
        print(f"Processing Time: {stats['processing_time']:.2f} seconds")
    
    if 'total_blocks_extracted' in stats:
        print(f"Total Blocks Extracted: {stats['total_blocks_extracted']:,}")
        print(f"Total Blocks Loaded: {stats['total_blocks_loaded']:,}")
        print(f"Total Processing Time: {stats['total_processing_time']:.2f} seconds")
        print(f"Batches Processed: {stats['batches_processed']}")
    
    if 'success' in stats:
        status = "✅ SUCCESS" if stats['success'] else "❌ FAILED"
        print(f"Status: {status}")
    
    if 'error' in stats:
        print(f"Error: {stats['error']}")
    
    print("="*50)


if __name__ == "__main__":
    main() 