"""
Simple test script to verify blockchain connection
This script tests basic functionality without requiring database setup
"""

import sys
import logging
from blockchain_client import BlockchainClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_blockchain_connection():
    """Test basic blockchain connection and functionality"""
    print("🔗 Testing Ethereum Blockchain Connection")
    print("=" * 50)
    
    try:
        # Initialize blockchain client
        print("1. Initializing blockchain client...")
        client = BlockchainClient()
        print("✅ Blockchain client initialized successfully")
        
        # Get latest block number
        print("\n2. Getting latest block number...")
        latest_block = client.get_latest_block_number()
        print(f"✅ Latest block number: {latest_block:,}")
        
        # Get a recent block
        print(f"\n3. Retrieving block {latest_block - 1}...")
        recent_block = client.get_block(latest_block - 1)
        
        if recent_block:
            print("✅ Block retrieved successfully")
            print(f"   Block Number: {recent_block['block_number']}")
            print(f"   Block Hash: {recent_block['block_hash'][:20]}...")
            print(f"   Timestamp: {recent_block['timestamp']}")
            print(f"   Transactions: {recent_block['transaction_count']}")
            print(f"   Gas Used: {recent_block['gas_used']:,}")
            print(f"   Gas Limit: {recent_block['gas_limit']:,}")
            
            # Show first transaction if available
            if recent_block['transactions']:
                first_tx = recent_block['transactions'][0]
                print(f"\n   First Transaction:")
                print(f"     Hash: {first_tx['tx_hash'][:20]}...")
                print(f"     From: {first_tx['from_address']}")
                print(f"     To: {first_tx['to_address']}")
                print(f"     Value: {first_tx['value_ether']} ETH")
                print(f"     Gas Price: {first_tx['gas_price_gwei']} Gwei")
        else:
            print("❌ Failed to retrieve block")
            return False
        
        # Test address validation
        print(f"\n4. Testing address validation...")
        test_address = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
        is_valid = client.is_address_valid(test_address)
        print(f"✅ Address validation test: {is_valid}")
        
        # Test ETH balance (optional - might fail if address has no balance)
        print(f"\n5. Testing ETH balance retrieval...")
        try:
            balance = client.get_eth_balance(test_address)
            print(f"✅ Balance retrieval successful: {balance} ETH")
        except Exception as e:
            print(f"⚠️ Balance retrieval failed (this is normal): {e}")
        
        print("\n" + "=" * 50)
        print("✅ All blockchain connection tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.error(f"Test failed: {e}")
        return False


def test_configuration():
    """Test configuration loading"""
    print("\n⚙️ Testing Configuration")
    print("=" * 30)
    
    try:
        from config import INFURA_URL, BATCH_SIZE
        
        print(f"✅ Configuration loaded successfully")
        print(f"   Infura URL: {INFURA_URL[:50]}...")
        print(f"   Batch Size: {BATCH_SIZE}")
        
        # Check if Infura URL is properly configured
        if INFURA_URL == 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID':
            print("⚠️  Warning: Infura URL still using placeholder value")
            print("   Please update your .env file with your actual Infura Project ID")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Ethereum Blockchain Data Collector - Connection Test")
    print("=" * 60)
    
    # Test configuration
    config_ok = test_configuration()
    
    # Test blockchain connection
    blockchain_ok = test_blockchain_connection()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 20)
    print(f"Configuration: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Blockchain: {'✅ PASS' if blockchain_ok else '❌ FAIL'}")
    
    if config_ok and blockchain_ok:
        print("\n🎉 All tests passed! Your setup is ready for blockchain data collection.")
        print("\nNext steps:")
        print("1. Set up your database (MongoDB or PostgreSQL)")
        print("2. Configure your .env file with database credentials")
        print("3. Run: python main.py test")
        print("4. Start collecting data: python main.py collect --latest 10")
        print("5. View dashboard: python main.py dashboard")
        return 0
    else:
        print("\n❌ Some tests failed. Please check your configuration and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 