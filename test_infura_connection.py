"""
Test Infura Connection
Simple script to test the Infura connection and verify it's working properly
"""

import os
from dotenv import load_dotenv
from blockchain_client import BlockchainClient
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_infura_connection():
    """Test the Infura connection"""
    try:
        # Check if INFURA_URL is set
        infura_url = os.getenv('INFURA_URL')
        if not infura_url or infura_url == 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID':
            print("❌ INFURA_URL not set or still using placeholder value")
            print("Please set your Infura Project ID in the .env file")
            print("Example: INFURA_URL=https://mainnet.infura.io/v3/YOUR_ACTUAL_PROJECT_ID")
            return False
        
        print(f"🔗 Testing connection to: {infura_url}")
        
        # Initialize blockchain client
        client = BlockchainClient()
        
        # Test basic connection
        latest_block = client.get_latest_block_number()
        print(f"✅ Successfully connected to Ethereum network")
        print(f"📦 Latest block number: {latest_block}")
        
        # Test getting a recent block
        recent_block = client.get_block(latest_block - 1)
        if recent_block:
            print(f"✅ Successfully retrieved block {recent_block['block_number']}")
            print(f"📊 Block has {recent_block['transaction_count']} transactions")
            
            # Test getting transaction details
            if recent_block['transactions']:
                first_tx = recent_block['transactions'][0]
                print(f"✅ Successfully retrieved transaction details")
                print(f"🔗 Transaction hash: {first_tx['tx_hash'][:20]}...")
                print(f"💰 Value: {first_tx['value_ether']} ETH")
        
        print("\n🎉 All tests passed! Infura connection is working properly.")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Infura connection: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure you have a valid Infura Project ID")
        print("2. Check that your .env file contains the correct INFURA_URL")
        print("3. Verify your internet connection")
        print("4. Check if you've reached your Infura rate limits")
        return False

if __name__ == "__main__":
    print("🧪 Testing Infura Connection...")
    print("=" * 50)
    
    success = test_infura_connection()
    
    if success:
        print("\n✅ Ready to use Infura for your Ethereum blockchain project!")
    else:
        print("\n❌ Please fix the connection issues before proceeding.") 