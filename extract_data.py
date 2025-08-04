"""
Simple Data Extraction Script
Demonstrates focused blockchain data extraction
"""

import json
import time
from focused_extractor import FocusedDataExtractor


def main():
    """Main function to demonstrate data extraction"""
    
    print("🔍 Focused Blockchain Data Extractor")
    print("=" * 50)
    
    # Initialize extractor
    try:
        extractor = FocusedDataExtractor()
        print("✅ Connected to Ethereum network")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    # Get latest block
    latest_block = extractor.get_latest_block_number()
    print(f"📊 Latest block: {latest_block:,}")
    
    # Extract data from a recent block
    target_block = latest_block - 1
    print(f"\n🔍 Extracting data from block {target_block:,}")
    
    # Extract block headers only
    print("\n1️⃣ Extracting Block Headers...")
    headers = extractor.extract_block_headers(target_block)
    if headers:
        print(f"   ✅ Block {headers['block_number']:,}")
        print(f"   📅 Timestamp: {headers['timestamp']}")
        print(f"   ⛏️  Miner: {headers['miner']}")
        print(f"   🔥 Gas Used: {headers['gas_used']:,}")
        print(f"   📝 Transactions: {headers['transaction_count']}")
    
    # Extract transactions
    print("\n2️⃣ Extracting Transactions...")
    transactions = extractor.extract_transactions(target_block)
    print(f"   ✅ Found {len(transactions)} transactions")
    
    if transactions:
        # Show first few transactions
        for i, tx in enumerate(transactions[:3]):
            print(f"   📄 TX {i+1}: {tx['tx_hash'][:20]}...")
            print(f"      From: {tx['from_address']}")
            print(f"      To: {tx['to_address']}")
            print(f"      Value: {tx['value_ether']} ETH")
            print(f"      Gas: {tx['gas']:,} (Price: {tx['gas_price_gwei']} Gwei)")
            print()
    
    # Optional: Extract token transfers
    print("\n3️⃣ Extracting Token Transfers (Optional)...")
    token_transfers = []
    for tx in transactions[:5]:  # Check first 5 transactions for efficiency
        transfers = extractor.extract_token_transfers(tx['tx_hash'])
        token_transfers.extend(transfers)
    
    print(f"   ✅ Found {len(token_transfers)} token transfers")
    for transfer in token_transfers[:3]:
        print(f"   🪙 Token: {transfer['token_address']}")
        print(f"      From: {transfer['from_address']}")
        print(f"      To: {transfer['to_address']}")
        print(f"      Value: {transfer['value']}")
        print()
    
    # Optional: Extract smart contract calls
    print("\n4️⃣ Extracting Smart Contract Calls (Optional)...")
    contract_calls = []
    for tx in transactions[:5]:  # Check first 5 transactions for efficiency
        call_data = extractor.extract_smart_contract_calls(tx['tx_hash'])
        if call_data:
            contract_calls.append(call_data)
    
    print(f"   ✅ Found {len(contract_calls)} smart contract calls")
    for call in contract_calls[:3]:
        print(f"   📋 Contract: {call['contract_address']}")
        print(f"      Function: {call['function_signature']}")
        print(f"      Status: {'✅ Success' if call['status'] == 1 else '❌ Failed'}")
        print(f"      Gas Used: {call['gas_used']:,}")
        print(f"      Logs: {call['logs_count']}")
        print()
    
    # Complete extraction example
    print("\n5️⃣ Complete Data Extraction...")
    complete_data = extractor.extract_block_data(
        target_block,
        include_token_transfers=True,
        include_contract_calls=True
    )
    
    if complete_data:
        print(f"   ✅ Complete extraction successful")
        print(f"   📊 Block Headers: ✅")
        print(f"   📄 Transactions: {len(complete_data['transactions'])}")
        print(f"   🪙 Token Transfers: {len(complete_data.get('token_transfers', []))}")
        print(f"   📋 Smart Contract Calls: {len(complete_data.get('smart_contract_calls', []))}")
        
        # Save to JSON file
        filename = f"block_{target_block}_data.json"
        with open(filename, 'w') as f:
            json.dump(complete_data, f, indent=2, default=str)
        print(f"   💾 Data saved to {filename}")
    
    print("\n🎉 Data extraction completed!")


if __name__ == "__main__":
    main() 