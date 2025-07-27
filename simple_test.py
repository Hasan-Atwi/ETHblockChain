"""
Simple test script with hardcoded Infura URL for testing
"""

import sys
import logging
from web3 import Web3

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_blockchain_connection():
    """Test basic blockchain connection and functionality"""
    print("🔗 Testing Ethereum Blockchain Connection")
    print("=" * 50)
    
    try:
        # Use a public Infura endpoint for testing
        infura_url = "https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"
        
        # Initialize Web3
        print("1. Initializing Web3 connection...")
        w3 = Web3(Web3.HTTPProvider(infura_url))
        
        if w3.is_connected():
            print("✅ Successfully connected to Ethereum network")
        else:
            print("❌ Failed to connect to Ethereum network")
            return False
        
        # Get latest block number
        print("\n2. Getting latest block number...")
        latest_block = w3.eth.block_number
        print(f"✅ Latest block number: {latest_block:,}")
        
        # Get a recent block
        print(f"\n3. Retrieving block {latest_block - 1}...")
        recent_block = w3.eth.get_block(latest_block - 1, full_transactions=True)
        
        if recent_block:
            print("✅ Block retrieved successfully")
            print(f"   Block Number: {recent_block['number']}")
            print(f"   Block Hash: {recent_block['hash'].hex()[:20]}...")
            print(f"   Timestamp: {recent_block['timestamp']}")
            print(f"   Transactions: {len(recent_block['transactions'])}")
            print(f"   Gas Used: {recent_block['gasUsed']:,}")
            print(f"   Gas Limit: {recent_block['gasLimit']:,}")
            
            # Show first transaction if available
            if recent_block['transactions']:
                first_tx = recent_block['transactions'][0]
                print(f"\n   First Transaction:")
                print(f"     Hash: {first_tx['hash'].hex()[:20]}...")
                print(f"     From: {first_tx['from']}")
                print(f"     To: {first_tx['to']}")
                print(f"     Value: {w3.from_wei(first_tx['value'], 'ether')} ETH")
                print(f"     Gas Price: {w3.from_wei(first_tx['gasPrice'], 'gwei')} Gwei")
        else:
            print("❌ Failed to retrieve block")
            return False
        
        # Test address validation
        print(f"\n4. Testing address validation...")
        test_address = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6"
        is_valid = w3.is_address(test_address)
        print(f"✅ Address validation test: {is_valid}")
        
        # Test ETH balance (optional - might fail if address has no balance)
        print(f"\n5. Testing ETH balance retrieval...")
        try:
            balance_wei = w3.eth.get_balance(test_address)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            print(f"✅ Balance retrieval successful: {balance_eth} ETH")
        except Exception as e:
            print(f"⚠️ Balance retrieval failed (this is normal): {e}")
        
        print("\n" + "=" * 50)
        print("✅ All blockchain connection tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.error(f"Test failed: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Ethereum Blockchain Data Collector - Simple Connection Test")
    print("=" * 60)
    
    # Test blockchain connection
    blockchain_ok = test_blockchain_connection()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 20)
    print(f"Blockchain: {'✅ PASS' if blockchain_ok else '❌ FAIL'}")
    
    if blockchain_ok:
        print("\n🎉 All tests passed! Your blockchain connection is working.")
        print("\nNext steps:")
        print("1. Get your own Infura API key")
        print("2. Set up your .env file with your credentials")
        print("3. Install additional dependencies: pip install -r requirements.txt")
        print("4. Set up database (MongoDB or PostgreSQL)")
        print("5. Start collecting data: python main.py collect --latest 10")
        return 0
    else:
        print("\n❌ Tests failed. Please check your internet connection and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 