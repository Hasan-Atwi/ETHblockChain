"""
Streamlit Dashboard for Blockchain Data Visualization
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from database import DatabaseManager
from blockchain_client import BlockchainClient
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Ethereum Blockchain Data Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database connection
@st.cache_resource
def get_db_manager():
    """Get database manager instance"""
    return DatabaseManager(use_postgres=True, use_mongodb=False)  # Use PostgreSQL

@st.cache_resource
def get_blockchain_client():
    """Get blockchain client instance"""
    return BlockchainClient()

def main():
    """Main dashboard function"""
    
    # Header
    st.title("📊 Ethereum Blockchain Data Dashboard")
    st.markdown("Real-time blockchain data collection and analysis")
    
    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Overview", "Block Explorer", "Transaction Analysis", "Token Transfers", "Smart Contracts", "Network Statistics", "Data Collection"]
    )
    
    # Initialize connections
    try:
        db_manager = get_db_manager()
        blockchain_client = get_blockchain_client()
    except Exception as e:
        st.error(f"Failed to connect to database or blockchain: {e}")
        return
    
    # Page routing
    if page == "Overview":
        show_overview(db_manager, blockchain_client)
    elif page == "Block Explorer":
        show_block_explorer(db_manager, blockchain_client)
    elif page == "Transaction Analysis":
        show_transaction_analysis(db_manager)
    elif page == "Token Transfers":
        show_token_transfers_page(db_manager, blockchain_client)
    elif page == "Smart Contracts":
        show_smart_contracts_page(db_manager, blockchain_client)
    elif page == "Network Statistics":
        show_network_statistics(db_manager)
    elif page == "Data Collection":
        show_data_collection(db_manager, blockchain_client)

def show_overview(db_manager, blockchain_client):
    """Show overview dashboard"""
    st.header("📈 Overview")
    
    # Get latest blockchain info
    try:
        latest_block_num = blockchain_client.get_latest_block_number()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Latest Block", f"#{latest_block_num:,}")
        
        with col2:
            # Get total blocks in database
            total_blocks = db_manager.get_total_blocks_count()
            st.metric("Blocks Collected", f"{total_blocks:,}")
        
        with col3:
            # Get total transactions in database
            total_transactions = db_manager.get_total_transactions_count()
            st.metric("Transactions Collected", f"{total_transactions:,}")
        
        with col4:
            # Get latest block from database
            latest_db_block = db_manager.get_latest_block_from_db()
            if latest_db_block:
                st.metric("Last Updated", f"Block #{latest_db_block['block_number']:,}")
            else:
                st.metric("Last Updated", "No data")
    
    except Exception as e:
        st.error(f"Error getting blockchain data: {e}")
    
    # Recent blocks chart
    st.subheader("Recent Blocks")
    try:
        # Get last 50 blocks
        recent_blocks = db_manager.get_recent_blocks(50)
        
        if recent_blocks:
            df_blocks = pd.DataFrame(recent_blocks)
            df_blocks['timestamp'] = pd.to_datetime(df_blocks['timestamp'], unit='s')
            
            # Gas usage over time
            fig_gas = px.line(
                df_blocks, 
                x='timestamp', 
                y='gas_used',
                title="Gas Usage Over Time",
                labels={'gas_used': 'Gas Used', 'timestamp': 'Time'}
            )
            st.plotly_chart(fig_gas, use_container_width=True)
            
            # Transaction count over time
            fig_tx = px.bar(
                df_blocks,
                x='timestamp',
                y='transaction_count',
                title="Transaction Count per Block",
                labels={'transaction_count': 'Transactions', 'timestamp': 'Time'}
            )
            st.plotly_chart(fig_tx, use_container_width=True)
        else:
            st.info("No block data available. Start data collection first.")
    
    except Exception as e:
        st.error(f"Error creating charts: {e}")

def show_block_explorer(db_manager, blockchain_client):
    """Show block explorer"""
    st.header("🔍 Block Explorer")
    
    # Debug section
    with st.expander("🔧 Debug Information"):
        st.write("**Database Status:**")
        try:
            total_blocks = db_manager.get_total_blocks_count()
            total_transactions = db_manager.get_total_transactions_count()
            st.write(f"- Total blocks in database: {total_blocks}")
            st.write(f"- Total transactions in database: {total_transactions}")
            
            if total_blocks > 0:
                latest_block = db_manager.get_latest_block_from_db()
                if latest_block:
                    st.write(f"- Latest block: #{latest_block['block_number']}")
                    
                    # Test getting this block with transactions
                    test_block = db_manager.get_block(latest_block['block_number'], include_transactions=True)
                    if test_block and 'transactions' in test_block:
                        st.write(f"- Latest block has {len(test_block['transactions'])} transactions stored")
                        # Show first few transaction hashes as proof
                        if test_block['transactions']:
                            st.write(f"- Sample transaction hashes:")
                            for i, tx in enumerate(test_block['transactions'][:3]):
                                st.write(f"  • TX {i+1}: {tx['tx_hash'][:20]}...")
                    else:
                        st.write(f"- Latest block has no transaction data stored")
                        st.warning("⚠️ This indicates transactions weren't collected with the block data")
            else:
                st.write("- No blocks found. Please collect some data first.")
                
        except Exception as e:
            st.error(f"Error getting debug info: {e}")
    
    # Block search
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_option = st.selectbox(
            "Search by:",
            ["Block Number", "Block Hash", "Latest Blocks"]
        )
    
    with col2:
        if search_option == "Latest Blocks":
            num_blocks = st.number_input("Number of blocks", min_value=1, max_value=100, value=10)
        else:
            search_value = st.text_input("Enter value:")
    
    # Search functionality
    if st.button("Search"):
        try:
            if search_option == "Block Number" and search_value:
                block_num = int(search_value)
                block_data = db_manager.get_block(block_num, include_transactions=True)
                if block_data:
                    display_block_details(block_data)
                else:
                    st.warning(f"Block {block_num} not found in database")
            
            elif search_option == "Block Hash" and search_value:
                block_data = db_manager.get_block_by_hash(search_value)
                if block_data:
                    display_block_details(block_data)
                else:
                    st.warning(f"Block with hash {search_value} not found in database")
                    st.info("💡 Tip: Make sure you've collected this block first!")
            
            elif search_option == "Latest Blocks":
                # Get blocks with transactions included
                blocks = db_manager.get_recent_blocks(num_blocks, include_transactions=True)
                
                if blocks:
                    st.success(f"Found {len(blocks)} blocks in database")
                    display_blocks_table(blocks)
                else:
                    st.info("No blocks found in database")
                    st.write("💡 **Try collecting some data first:**")
                    st.write("1. Go to 'Data Collection' page")
                    st.write("2. Select 'Latest Blocks' and collect 5-10 blocks")
                    st.write("3. Come back here to view the blocks with transaction hashes")
        
        except Exception as e:
            st.error(f"Error searching blocks: {e}")

def display_block_details(block_data):
    """Display detailed block information"""
    st.subheader(f"Block #{block_data['block_number']}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Block Information:**")
        st.write(f"Hash: `{block_data['block_hash']}`")
        st.write(f"Parent Hash: `{block_data['parent_hash']}`")
        st.write(f"Timestamp: {datetime.fromtimestamp(block_data['timestamp'])}")
        st.write(f"Miner: `{block_data['miner']}`")
    
    with col2:
        st.write("**Block Statistics:**")
        st.write(f"Difficulty: {block_data['difficulty']:,}")
        st.write(f"Gas Limit: {block_data['gas_limit']:,}")
        st.write(f"Gas Used: {block_data['gas_used']:,}")
        st.write(f"Transactions: {block_data['transaction_count']}")
    
    # Show transactions if available
    if 'transactions' in block_data and block_data['transactions']:
        st.subheader("Transactions")
        display_transactions_table(block_data['transactions'])

def display_blocks_table(blocks):
    """Display blocks in a table with transaction hashes"""
    # First, get full block data with transactions for all blocks
    db_manager = get_db_manager()
    enriched_blocks = []
    
    # Debug information
    st.write("🔍 **Debug Information:**")
    
    for block in blocks:
        try:
            # Get full block data with transactions
            full_block_data = db_manager.get_block(block['block_number'], include_transactions=True)
            
            # Debug output
            st.write(f"Block #{block['block_number']}:")
            st.write(f"- Original block has {block.get('transaction_count', 0)} transactions")
            
            if full_block_data:
                st.write(f"- Retrieved block data: ✅")
                if 'transactions' in full_block_data and full_block_data['transactions']:
                    st.write(f"- Transactions in retrieved data: {len(full_block_data['transactions'])}")
                    # Show sample transaction hashes
                    sample_tx = full_block_data['transactions'][0]
                    st.write(f"- Sample TX hash: {sample_tx['tx_hash'][:20]}...")
                else:
                    st.write(f"- No transactions found in retrieved data")
                    st.warning("⚠️ Block was collected without transaction data")
                enriched_blocks.append(full_block_data)
            else:
                st.write(f"- Failed to retrieve full block data ❌")
                enriched_blocks.append(block)  # Fallback to original block data
                
        except Exception as e:
            st.error(f"Error enriching block {block['block_number']}: {e}")
            enriched_blocks.append(block)  # Fallback to original block data
    
    # Create the main blocks table
    df = pd.DataFrame(blocks)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df = df[['block_number', 'block_hash', 'timestamp', 'transaction_count', 'gas_used']]
    df.columns = ['Block #', 'Block Hash', 'Timestamp', 'Tx Count', 'Gas Used']
    
    st.dataframe(df, use_container_width=True)
    
    # Show transaction hashes for each block
    st.subheader("📋 Transaction Hashes by Block")
    
    for block_data in enriched_blocks:
        block_num = block_data['block_number']
        
        if 'transactions' in block_data and block_data['transactions']:
            transactions = block_data['transactions']
            
            with st.expander(f"Block #{block_num} - {len(transactions)} Transaction Hashes", expanded=True):
                
                # Create a table with transaction hashes and basic info
                tx_data = []
                for tx in transactions:
                    tx_data.append({
                        'Index': tx.get('transaction_index', 0),
                        'Transaction Hash': tx['tx_hash'],
                        'From': tx['from_address'][:10] + '...' if tx['from_address'] else 'N/A',
                        'To': tx['to_address'][:10] + '...' if tx['to_address'] else 'Contract Creation',
                        'Value (ETH)': f"{float(tx['value_ether']):.6f}" if tx['value_ether'] else '0',
                        'Gas Price (Gwei)': f"{float(tx['gas_price_gwei']):.2f}" if tx['gas_price_gwei'] else '0'
                    })
                
                # Display transaction table
                tx_df = pd.DataFrame(tx_data)
                st.dataframe(tx_df, use_container_width=True)
                
                # Add analyze buttons for first few transactions
                st.write("**Quick Analysis:**")
                cols = st.columns(min(5, len(transactions)))
                for i, tx in enumerate(transactions[:5]):
                    with cols[i]:
                        if st.button(f"Analyze TX #{i+1}", key=f"analyze_block_{block_num}_tx_{i}"):
                            st.session_state['selected_tx_hash'] = tx['tx_hash']
                            st.success("✅ Transaction selected! Go to Transaction Analysis tab.")
                
                # Show copyable transaction hashes
                st.write("**Copy Transaction Hashes:**")
                for i, tx in enumerate(transactions[:10]):  # Show first 10
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.code(tx['tx_hash'], language='text')
                    with col2:
                        if st.button(f"Analyze", key=f"analyze_copy_{block_num}_{i}"):
                            st.session_state['selected_tx_hash'] = tx['tx_hash']
                            st.success("✅ Hash selected! Go to Transaction Analysis.")
        else:
            with st.expander(f"Block #{block_num} - No transaction data available"):
                st.warning("⚠️ Transaction data not found for this block.")
                st.info("💡 **Possible reasons:**")
                st.write("- Block was collected without full transaction details")
                st.write("- Database connection issue during collection")
                st.write("- Block contains 0 transactions")
                
                # Add a button to check if transactions exist separately
                if st.button(f"Check for transactions in Block #{block_num}", key=f"check_tx_{block_num}"):
                    try:
                        if db_manager.use_postgres:
                            session = db_manager.PostgresSession()
                            from database import Transaction
                            tx_count = session.query(Transaction).filter(
                                Transaction.block_number == block_num
                            ).count()
                            session.close()
                            if tx_count > 0:
                                st.success(f"Found {tx_count} transactions in database for this block!")
                                st.info("The issue is with data retrieval, not storage.")
                            else:
                                st.warning("No transactions found in database for this block.")
                        elif db_manager.use_mongodb:
                            tx_count = db_manager.transactions_collection.count_documents(
                                {'block_number': block_num}
                            )
                            if tx_count > 0:
                                st.success(f"Found {tx_count} transactions in database for this block!")
                                st.info("The issue is with data retrieval, not storage.")
                            else:
                                st.warning("No transactions found in database for this block.")
                    except Exception as e:
                        st.error(f"Error checking transactions: {e}")

def show_transaction_analysis(db_manager):
    """Show transaction analysis"""
    st.header("💸 Transaction Analysis")
    
    # Check if transaction hash was passed from Block Explorer
    if 'selected_tx_hash' in st.session_state:
        default_hash = st.session_state['selected_tx_hash']
        del st.session_state['selected_tx_hash']  # Clear after use
    else:
        default_hash = ""
    
    # Transaction search
    tx_hash = st.text_input("Enter transaction hash:", value=default_hash)
    
    if st.button("Search Transaction") or default_hash:
        if tx_hash:
            try:
                tx_data = db_manager.get_transaction(tx_hash)
                if tx_data:
                    display_transaction_details(tx_data, db_manager)
                    
                    # Add token transfers analysis
                    show_token_transfers_for_transaction(tx_hash, db_manager)
                    
                    # Add smart contract analysis
                    show_smart_contract_analysis_for_transaction(tx_hash, db_manager)
                else:
                    st.warning("Transaction not found in database")
                    st.info("💡 Tip: Make sure you've collected the block containing this transaction first!")
            except Exception as e:
                st.error(f"Error searching transaction: {e}")
    
    # Transaction statistics
    st.subheader("📊 Transaction Statistics")
    
    try:
        # Get recent transactions
        recent_txs = db_manager.get_recent_transactions(1000)
        
        if recent_txs:
            df_txs = pd.DataFrame(recent_txs)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Value distribution
                fig_value = px.histogram(
                    df_txs,
                    x='value_ether',
                    nbins=50,
                    title="Transaction Value Distribution (ETH)",
                    labels={'value_ether': 'Value (ETH)', 'count': 'Count'}
                )
                fig_value.update_xaxes(range=[0, df_txs['value_ether'].quantile(0.95)])
                st.plotly_chart(fig_value, use_container_width=True)
            
            with col2:
                # Gas price distribution
                fig_gas = px.histogram(
                    df_txs,
                    x='gas_price_gwei',
                    nbins=50,
                    title="Gas Price Distribution (Gwei)",
                    labels={'gas_price_gwei': 'Gas Price (Gwei)', 'count': 'Count'}
                )
                st.plotly_chart(fig_gas, use_container_width=True)
            
            # Transaction types analysis
            st.subheader("🔍 Transaction Types Analysis")
            
            # Categorize transactions
            df_txs['tx_type'] = df_txs.apply(categorize_transaction, axis=1)
            tx_type_counts = df_txs['tx_type'].value_counts()
            
            fig_types = px.pie(
                values=tx_type_counts.values,
                names=tx_type_counts.index,
                title="Transaction Types Distribution"
            )
            st.plotly_chart(fig_types, use_container_width=True)
        
        else:
            st.info("No transaction data available. Start data collection first!")
    
    except Exception as e:
        st.error(f"Error creating transaction charts: {e}")

def display_transaction_details(tx_data, db_manager=None):
    """Display detailed transaction information"""
    st.subheader("🔍 Transaction Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Transaction Information:**")
        st.code(tx_data['tx_hash'], language='text')
        st.write(f"**Block:** #{tx_data['block_number']}")
        st.write(f"**From:** `{tx_data['from_address']}`")
        st.write(f"**To:** `{tx_data['to_address'] if tx_data['to_address'] else 'Contract Creation'}`")
        st.write(f"**Transaction Index:** {tx_data.get('transaction_index', 'N/A')}")
    
    with col2:
        st.write("**Transaction Details:**")
        st.write(f"**Value:** {tx_data['value_ether']} ETH")
        st.write(f"**Gas Limit:** {tx_data['gas']:,}")
        st.write(f"**Gas Price:** {tx_data['gas_price_gwei']} Gwei")
        st.write(f"**Nonce:** {tx_data['nonce']}")
        
        # Calculate transaction fee
        gas_fee_eth = float(tx_data['gas']) * float(tx_data['gas_price_gwei']) / 1e9
        st.write(f"**Max Fee:** {gas_fee_eth:.6f} ETH")
    
    # Show input data if available
    if tx_data.get('input_data') and tx_data['input_data'] != '0x':
        st.write("**Input Data:**")
        st.code(tx_data['input_data'][:200] + ('...' if len(tx_data['input_data']) > 200 else ''), language='text')
        
        # Determine transaction type
        tx_type = categorize_transaction(tx_data)
        st.write(f"**Transaction Type:** {tx_type}")
    else:
        st.write("**Transaction Type:** Simple ETH Transfer")

def display_transactions_table(transactions):
    """Display transactions in a table"""
    df = pd.DataFrame(transactions)
    df = df[['tx_hash', 'from_address', 'to_address', 'value_ether', 'gas_price_gwei']]
    df.columns = ['Transaction Hash', 'From', 'To', 'Value (ETH)', 'Gas Price (Gwei)']
    
    # Make transaction hashes clickable/copyable
    st.dataframe(df, use_container_width=True)
    
    # Add a section to easily copy transaction hashes
    if len(transactions) > 0:
        st.subheader("📋 Transaction Hashes (Click to Copy)")
        for i, tx in enumerate(transactions[:10]):  # Show first 10
            col1, col2 = st.columns([3, 1])
            with col1:
                st.code(tx['tx_hash'], language='text')
            with col2:
                if st.button(f"Analyze", key=f"analyze_{i}"):
                    st.session_state['selected_tx_hash'] = tx['tx_hash']
                    st.success(f"Transaction hash copied! Go to Transaction Analysis tab.")

def show_network_statistics(db_manager):
    """Show network statistics"""
    st.header("🌐 Network Statistics")
    
    try:
        # Get all blocks
        all_blocks = db_manager.get_all_blocks()
        
        if all_blocks:
            df_blocks = pd.DataFrame(all_blocks)
            df_blocks['timestamp'] = pd.to_datetime(df_blocks['timestamp'], unit='s')
            
            # Network activity over time
            st.subheader("Network Activity")
            
            # Daily transaction count
            df_blocks['date'] = df_blocks['timestamp'].dt.date
            daily_txs = df_blocks.groupby('date')['transaction_count'].sum().reset_index()
            
            fig_daily = px.line(
                daily_txs,
                x='date',
                y='transaction_count',
                title="Daily Transaction Count",
                labels={'transaction_count': 'Transactions', 'date': 'Date'}
            )
            st.plotly_chart(fig_daily, use_container_width=True)
            
            # Block time analysis
            df_blocks = df_blocks.sort_values('timestamp')
            df_blocks['block_time'] = df_blocks['timestamp'].diff().dt.total_seconds()
            
            fig_block_time = px.histogram(
                df_blocks.dropna(),
                x='block_time',
                nbins=50,
                title="Block Time Distribution (seconds)",
                labels={'block_time': 'Block Time (seconds)', 'count': 'Count'}
            )
            st.plotly_chart(fig_block_time, use_container_width=True)
            
            # Gas usage statistics
            st.subheader("Gas Usage Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_gas = df_blocks['gas_used'].mean()
                st.metric("Average Gas Used", f"{avg_gas:,.0f}")
            
            with col2:
                max_gas = df_blocks['gas_used'].max()
                st.metric("Maximum Gas Used", f"{max_gas:,.0f}")
            
            with col3:
                avg_gas_limit = df_blocks['gas_limit'].mean()
                st.metric("Average Gas Limit", f"{avg_gas_limit:,.0f}")
        
        else:
            st.info("No network data available")
    
    except Exception as e:
        st.error(f"Error creating network statistics: {e}")

def show_token_transfers_page(db_manager, blockchain_client):
    """Show token transfers analysis page"""
    st.header("🪙 Token Transfers Analysis")
    
    st.write("Analyze ERC-20 token transfers and token activity on the Ethereum blockchain")
    
    # Token transfer search
    st.subheader("🔍 Search Token Transfers")
    
    search_type = st.selectbox(
        "Search by:",
        ["Transaction Hash", "Token Contract Address", "Wallet Address", "Recent Activity"]
    )
    
    if search_type == "Transaction Hash":
        tx_hash = st.text_input("Enter transaction hash:")
        if st.button("Search") and tx_hash:
            show_token_transfers_for_transaction(tx_hash, db_manager)
    
    elif search_type == "Token Contract Address":
        token_address = st.text_input("Enter token contract address:")
        if st.button("Search") and token_address:
            st.info("Token contract analysis feature coming soon!")
            # TODO: Implement token contract analysis
    
    elif search_type == "Wallet Address":
        wallet_address = st.text_input("Enter wallet address:")
        if st.button("Search") and wallet_address:
            st.info("Wallet token activity analysis feature coming soon!")
            # TODO: Implement wallet token activity
    
    elif search_type == "Recent Activity":
        st.subheader("📊 Recent Token Transfer Activity")
        
        # Get recent transactions and analyze for token transfers
        try:
            recent_txs = db_manager.get_recent_transactions(100)
            if recent_txs:
                token_tx_count = 0
                for tx in recent_txs:
                    if tx.get('input_data') and tx['input_data'] != '0x':
                        if (tx['input_data'].startswith('0xa9059cbb') or 
                            tx['input_data'].startswith('0x23b872dd')):
                            token_tx_count += 1
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Recent Transactions", len(recent_txs))
                with col2:
                    st.metric("Likely Token Transfers", token_tx_count)
                with col3:
                    percentage = (token_tx_count / len(recent_txs)) * 100 if recent_txs else 0
                    st.metric("Token Transfer %", f"{percentage:.1f}%")
                
                # Show sample token transfers
                st.subheader("Sample Token Transfer Transactions")
                token_txs = [tx for tx in recent_txs if tx.get('input_data', '').startswith(('0xa9059cbb', '0x23b872dd'))][:10]
                
                if token_txs:
                    for tx in token_txs:
                        with st.expander(f"Token Transfer: {tx['tx_hash'][:20]}..."):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Hash:** `{tx['tx_hash']}`")
                                st.write(f"**Block:** #{tx['block_number']}")
                            with col2:
                                st.write(f"**From:** `{tx['from_address']}`")
                                st.write(f"**To:** `{tx['to_address']}`")
                            
                            if st.button(f"Analyze", key=f"token_analyze_{tx['tx_hash'][:10]}"):
                                show_token_transfers_for_transaction(tx['tx_hash'], db_manager)
                else:
                    st.info("No recent token transfers found")
            else:
                st.info("No recent transaction data available")
        except Exception as e:
            st.error(f"Error analyzing recent token activity: {e}")

def show_smart_contracts_page(db_manager, blockchain_client):
    """Show smart contracts analysis page"""
    st.header("🔧 Smart Contract Analysis")
    
    st.write("Analyze smart contract interactions and calls on the Ethereum blockchain")
    
    # Smart contract search
    st.subheader("🔍 Search Smart Contract Activity")
    
    search_type = st.selectbox(
        "Search by:",
        ["Transaction Hash", "Contract Address", "Function Signature", "Recent Activity"]
    )
    
    if search_type == "Transaction Hash":
        tx_hash = st.text_input("Enter transaction hash:")
        if st.button("Search") and tx_hash:
            show_smart_contract_analysis_for_transaction(tx_hash, db_manager)
    
    elif search_type == "Contract Address":
        contract_address = st.text_input("Enter contract address:")
        if st.button("Search") and contract_address:
            st.info("Contract address analysis feature coming soon!")
            # TODO: Implement contract address analysis
    
    elif search_type == "Function Signature":
        function_sig = st.text_input("Enter function signature (e.g., 0xa9059cbb):")
        if st.button("Search") and function_sig:
            st.info("Function signature analysis feature coming soon!")
            # TODO: Implement function signature analysis
    
    elif search_type == "Recent Activity":
        st.subheader("📊 Recent Smart Contract Activity")
        
        try:
            recent_txs = db_manager.get_recent_transactions(100)
            if recent_txs:
                contract_tx_count = 0
                contract_creation_count = 0
                
                for tx in recent_txs:
                    if tx.get('input_data') and tx['input_data'] != '0x':
                        if tx.get('to_address'):
                            contract_tx_count += 1
                        else:
                            contract_creation_count += 1
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Recent Transactions", len(recent_txs))
                with col2:
                    st.metric("Contract Calls", contract_tx_count)
                with col3:
                    st.metric("Contract Creations", contract_creation_count)
                with col4:
                    percentage = (contract_tx_count / len(recent_txs)) * 100 if recent_txs else 0
                    st.metric("Contract Call %", f"{percentage:.1f}%")
                
                # Function signature analysis
                st.subheader("🔍 Popular Function Signatures")
                function_sigs = {}
                for tx in recent_txs:
                    if tx.get('input_data') and len(tx['input_data']) >= 10:
                        sig = tx['input_data'][:10]
                        function_sigs[sig] = function_sigs.get(sig, 0) + 1
                
                if function_sigs:
                    # Sort by frequency
                    sorted_sigs = sorted(function_sigs.items(), key=lambda x: x[1], reverse=True)[:10]
                    
                    for sig, count in sorted_sigs:
                        function_name = get_function_name_from_signature(sig)
                        col1, col2, col3 = st.columns([2, 2, 1])
                        with col1:
                            st.code(sig)
                        with col2:
                            st.write(function_name or "Unknown Function")
                        with col3:
                            st.write(f"{count} calls")
                
                # Show sample contract interactions
                st.subheader("Sample Contract Interactions")
                contract_txs = [tx for tx in recent_txs if tx.get('input_data', '') != '0x' and tx.get('to_address')][:10]
                
                if contract_txs:
                    for tx in contract_txs:
                        with st.expander(f"Contract Call: {tx['tx_hash'][:20]}..."):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Hash:** `{tx['tx_hash']}`")
                                st.write(f"**Contract:** `{tx['to_address']}`")
                            with col2:
                                st.write(f"**Function:** `{tx['input_data'][:10]}`")
                                function_name = get_function_name_from_signature(tx['input_data'][:10])
                                if function_name:
                                    st.write(f"**Likely Function:** {function_name}")
                            
                            if st.button(f"Analyze", key=f"contract_analyze_{tx['tx_hash'][:10]}"):
                                show_smart_contract_analysis_for_transaction(tx['tx_hash'], db_manager)
                else:
                    st.info("No recent contract interactions found")
            else:
                st.info("No recent transaction data available")
        except Exception as e:
            st.error(f"Error analyzing recent contract activity: {e}")

def show_data_collection(db_manager, blockchain_client):
    """Show data collection interface"""
    st.header("📥 Data Collection")
    
    st.write("Configure and run data collection from Ethereum blockchain")
    
    # Collection options
    st.subheader("Collection Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        collection_type = st.selectbox(
            "Collection Type:",
            ["Latest Blocks", "Historical Range", "Scheduled Collection"]
        )
    
    with col2:
        if collection_type == "Latest Blocks":
            num_blocks = st.number_input("Number of blocks", min_value=1, max_value=1000, value=10)
        elif collection_type == "Historical Range":
            start_block = st.number_input("Start block", min_value=0, value=0)
            end_block = st.number_input("End block", min_value=0, value=100)
    
    # Run collection
    if st.button("Start Collection"):
        try:
            from etl_pipeline import ETLPipeline
            
            pipeline = ETLPipeline(use_postgres=True, use_mongodb=False)
            
            with st.spinner("Collecting data..."):
                if collection_type == "Latest Blocks":
                    stats = pipeline.process_latest_blocks(num_blocks)
                elif collection_type == "Historical Range":
                    stats = pipeline.process_historical_blocks(start_block, end_block)
                else:
                    st.info("Scheduled collection not implemented in this demo")
                    return
            
            st.success(f"Collection completed!")
            st.json(stats)
            
            pipeline.close()
            
        except Exception as e:
            st.error(f"Error during collection: {e}")

def categorize_transaction(tx_data):
    """Categorize transaction based on input data and other properties"""
    if not tx_data.get('input_data') or tx_data['input_data'] == '0x':
        return "ETH Transfer"
    
    input_data = tx_data['input_data']
    
    # Check for common function signatures
    if input_data.startswith('0xa9059cbb'):
        return "ERC-20 Transfer"
    elif input_data.startswith('0x23b872dd'):
        return "ERC-20 TransferFrom"
    elif input_data.startswith('0x095ea7b3'):
        return "ERC-20 Approve"
    elif input_data.startswith('0x42842e0e') or input_data.startswith('0x23b872dd'):
        return "NFT Transfer"
    elif input_data.startswith('0x7ff36ab5'):
        return "Uniswap Swap"
    elif input_data.startswith('0x38ed1739'):
        return "Uniswap Swap (ETH)"
    elif not tx_data.get('to_address'):
        return "Contract Creation"
    else:
        return "Smart Contract Call"

def show_token_transfers_for_transaction(tx_hash, db_manager):
    """Show token transfers for a specific transaction"""
    st.subheader("🪙 Token Transfers")
    
    try:
        # Try to get token transfers from database (if implemented)
        # For now, we'll simulate this functionality
        blockchain_client = get_blockchain_client()
        
        # Get transaction receipt to analyze logs
        from web3.exceptions import TransactionNotFound
        try:
            receipt = blockchain_client.w3.eth.get_transaction_receipt(tx_hash)
            
            token_transfers = []
            transfer_event_signature = blockchain_client.w3.keccak(text="Transfer(address,address,uint256)").hex()
            
            for log in receipt['logs']:
                if len(log['topics']) >= 3 and log['topics'][0].hex() == transfer_event_signature:
                    try:
                        token_transfer = {
                            'token_address': log['address'],
                            'from_address': '0x' + log['topics'][1].hex()[-40:],
                            'to_address': '0x' + log['topics'][2].hex()[-40:],
                            'raw_amount': log['data'],
                            'log_index': log['logIndex']
                        }
                        token_transfers.append(token_transfer)
                    except Exception as e:
                        continue
            
            if token_transfers:
                st.success(f"Found {len(token_transfers)} token transfer(s)")
                
                for i, transfer in enumerate(token_transfers):
                    with st.expander(f"Token Transfer #{i+1}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Token Contract:** `{transfer['token_address']}`")
                            st.write(f"**From:** `{transfer['from_address']}`")
                        with col2:
                            st.write(f"**To:** `{transfer['to_address']}`")
                            st.write(f"**Log Index:** {transfer['log_index']}")
                        st.write(f"**Raw Amount Data:** `{transfer['raw_amount']}`")
            else:
                st.info("No token transfers found in this transaction")
                
        except TransactionNotFound:
            st.warning("Transaction not found on blockchain - it may not be confirmed yet")
        except Exception as e:
            st.error(f"Error analyzing token transfers: {e}")
            
    except Exception as e:
        st.error(f"Error getting token transfers: {e}")

def show_smart_contract_analysis_for_transaction(tx_hash, db_manager):
    """Show smart contract analysis for a specific transaction"""
    st.subheader("🔧 Smart Contract Analysis")
    
    try:
        blockchain_client = get_blockchain_client()
        
        # Get transaction and receipt
        tx = blockchain_client.w3.eth.get_transaction(tx_hash)
        receipt = blockchain_client.w3.eth.get_transaction_receipt(tx_hash)
        
        if tx['to'] and tx['input'] and tx['input'] != '0x':
            st.success("This is a smart contract interaction")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Contract Information:**")
                st.write(f"**Contract Address:** `{tx['to']}`")
                st.write(f"**Function Signature:** `{tx['input'][:10]}`")
                st.write(f"**Input Data Length:** {len(tx['input'])} characters")
            
            with col2:
                st.write("**Execution Details:**")
                st.write(f"**Gas Used:** {receipt['gasUsed']:,}")
                st.write(f"**Status:** {'✅ Success' if receipt['status'] == 1 else '❌ Failed'}")
                st.write(f"**Logs Generated:** {len(receipt['logs'])}")
            
            # Show function signature analysis
            function_sig = tx['input'][:10]
            function_name = get_function_name_from_signature(function_sig)
            if function_name:
                st.write(f"**Likely Function:** {function_name}")
            
            # Show logs if any
            if receipt['logs']:
                with st.expander(f"View {len(receipt['logs'])} Event Log(s)"):
                    for i, log in enumerate(receipt['logs']):
                        st.write(f"**Log #{i+1}:**")
                        st.write(f"- Address: `{log['address']}`")
                        st.write(f"- Topics: {len(log['topics'])}")
                        st.write(f"- Data: `{log['data'][:50]}...`")
                        st.write("---")
        else:
            st.info("This is a simple ETH transfer, not a smart contract interaction")
            
    except Exception as e:
        st.error(f"Error analyzing smart contract: {e}")

def get_function_name_from_signature(signature):
    """Get likely function name from 4-byte signature"""
    # Common function signatures
    signatures = {
        '0xa9059cbb': 'transfer(address,uint256)',
        '0x23b872dd': 'transferFrom(address,address,uint256)',
        '0x095ea7b3': 'approve(address,uint256)',
        '0x70a08231': 'balanceOf(address)',
        '0x18160ddd': 'totalSupply()',
        '0x7ff36ab5': 'swapExactETHForTokens(...)',
        '0x38ed1739': 'swapExactTokensForETH(...)',
        '0x42842e0e': 'safeTransferFrom(address,address,uint256)',
        '0xb88d4fde': 'safeTransferFrom(address,address,uint256,bytes)',
    }
    
    return signatures.get(signature, None)

if __name__ == "__main__":
    main() 