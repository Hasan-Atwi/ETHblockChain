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
    return DatabaseManager(use_postgres=False, use_mongodb=True)  # Use MongoDB for demo

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
        ["Overview", "Block Explorer", "Transaction Analysis", "Network Statistics", "Data Collection"]
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
            total_blocks = db_manager.blocks_collection.count_documents({})
            st.metric("Blocks Collected", f"{total_blocks:,}")
        
        with col3:
            # Get total transactions in database
            total_transactions = db_manager.transactions_collection.count_documents({})
            st.metric("Transactions Collected", f"{total_transactions:,}")
        
        with col4:
            # Get latest block from database
            latest_db_block = db_manager.blocks_collection.find_one(
                sort=[('block_number', -1)]
            )
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
        recent_blocks = list(db_manager.blocks_collection.find(
            sort=[('block_number', -1)]
        ).limit(50))
        
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
                block_data = db_manager.get_block(block_num)
                if block_data:
                    display_block_details(block_data)
                else:
                    st.warning(f"Block {block_num} not found in database")
            
            elif search_option == "Block Hash" and search_value:
                block_data = db_manager.blocks_collection.find_one({'block_hash': search_value})
                if block_data:
                    display_block_details(block_data)
                else:
                    st.warning(f"Block with hash {search_value} not found")
            
            elif search_option == "Latest Blocks":
                blocks = list(db_manager.blocks_collection.find(
                    sort=[('block_number', -1)]
                ).limit(num_blocks))
                
                if blocks:
                    display_blocks_table(blocks)
                else:
                    st.info("No blocks found in database")
        
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
    """Display blocks in a table"""
    df = pd.DataFrame(blocks)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df = df[['block_number', 'block_hash', 'timestamp', 'transaction_count', 'gas_used']]
    df.columns = ['Block #', 'Hash', 'Timestamp', 'Tx Count', 'Gas Used']
    
    st.dataframe(df, use_container_width=True)

def show_transaction_analysis(db_manager):
    """Show transaction analysis"""
    st.header("💸 Transaction Analysis")
    
    # Transaction search
    tx_hash = st.text_input("Enter transaction hash:")
    
    if st.button("Search Transaction"):
        if tx_hash:
            try:
                tx_data = db_manager.get_transaction(tx_hash)
                if tx_data:
                    display_transaction_details(tx_data)
                else:
                    st.warning("Transaction not found in database")
            except Exception as e:
                st.error(f"Error searching transaction: {e}")
    
    # Transaction statistics
    st.subheader("Transaction Statistics")
    
    try:
        # Get recent transactions
        recent_txs = list(db_manager.transactions_collection.find(
            sort=[('block_number', -1)]
        ).limit(1000))
        
        if recent_txs:
            df_txs = pd.DataFrame(recent_txs)
            
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
            
            # Gas price distribution
            fig_gas = px.histogram(
                df_txs,
                x='gas_price_gwei',
                nbins=50,
                title="Gas Price Distribution (Gwei)",
                labels={'gas_price_gwei': 'Gas Price (Gwei)', 'count': 'Count'}
            )
            st.plotly_chart(fig_gas, use_container_width=True)
        
        else:
            st.info("No transaction data available")
    
    except Exception as e:
        st.error(f"Error creating transaction charts: {e}")

def display_transaction_details(tx_data):
    """Display detailed transaction information"""
    st.subheader("Transaction Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Transaction Information:**")
        st.write(f"Hash: `{tx_data['tx_hash']}`")
        st.write(f"Block: #{tx_data['block_number']}")
        st.write(f"From: `{tx_data['from_address']}`")
        st.write(f"To: `{tx_data['to_address']}`")
    
    with col2:
        st.write("**Transaction Details:**")
        st.write(f"Value: {tx_data['value_ether']} ETH")
        st.write(f"Gas: {tx_data['gas']:,}")
        st.write(f"Gas Price: {tx_data['gas_price_gwei']} Gwei")
        st.write(f"Nonce: {tx_data['nonce']}")

def display_transactions_table(transactions):
    """Display transactions in a table"""
    df = pd.DataFrame(transactions)
    df = df[['tx_hash', 'from_address', 'to_address', 'value_ether', 'gas_price_gwei']]
    df.columns = ['Hash', 'From', 'To', 'Value (ETH)', 'Gas Price (Gwei)']
    
    st.dataframe(df, use_container_width=True)

def show_network_statistics(db_manager):
    """Show network statistics"""
    st.header("🌐 Network Statistics")
    
    try:
        # Get all blocks
        all_blocks = list(db_manager.blocks_collection.find())
        
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
            
            pipeline = ETLPipeline(use_postgres=False, use_mongodb=True)
            
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

if __name__ == "__main__":
    main() 