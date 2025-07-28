# 🚀 Ethereum Blockchain Data Collector

A comprehensive Python-based system for collecting, storing, and analyzing Ethereum blockchain data. This project implements a complete ETL (Extract, Transform, Load) pipeline for blockchain data collection with real-time monitoring and visualization capabilities.

## 📋 Project Overview

This blockchain data collector is designed to:
- **Connect** to Ethereum mainnet via Infura API
- **Extract** block and transaction data in real-time or from historical blocks
- **Transform** raw blockchain data into structured formats
- **Load** data into PostgreSQL and/or MongoDB databases
- **Visualize** data through an interactive Streamlit dashboard
- **Automate** data collection with scheduled ETL pipelines

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Ethereum      │    │   ETL Pipeline  │    │   Databases     │
│   Blockchain    │───▶│   (Python)      │───▶│   (PostgreSQL/  │
│   (Infura)      │    │                 │    │    MongoDB)     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Dashboard     │
                       │   (Streamlit)   │
                       └─────────────────┘
```

## 🔄 Code Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           APPLICATION START                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. CONFIGURATION LOADING                                                  │
│    ├── Load .env file (Infura URL, Database credentials)                  │
│    ├── Initialize logging configuration                                    │
│    └── Set up environment variables                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. BLOCKCHAIN CONNECTION                                                  │
│    ├── Initialize BlockchainClient                                        │
│    ├── Connect to Infura via Web3.py                                     │
│    ├── Verify connection (get latest block)                              │
│    └── Test address validation and balance queries                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. DATABASE SETUP                                                         │
│    ├── Initialize DatabaseManager                                         │
│    ├── Connect to PostgreSQL (if enabled)                                │
│    │   ├── Create tables (blocks, transactions)                         │
│    │   └── Set up SQLAlchemy ORM                                         │
│    └── Connect to MongoDB (if enabled)                                   │
│        ├── Create collections (blocks, transactions)                     │
│        └── Set up indexes for performance                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. DATA COLLECTION PIPELINE                                              │
│    ├── ETL Pipeline Initialization                                       │
│    │   ├── Set batch size and block range                               │
│    │   ├── Configure rate limiting                                       │
│    │   └── Initialize progress tracking                                  │
│    │                                                                      │
│    ├── EXTRACT PHASE                                                     │
│    │   ├── Get block data from Infura                                    │
│    │   ├── Retrieve transaction details                                  │
│    │   ├── Handle rate limits and retries                               │
│    │   └── Validate data integrity                                       │
│    │                                                                      │
│    ├── TRANSFORM PHASE                                                   │
│    │   ├── Format block data (hash, timestamp, gas info)                │
│    │   ├── Process transaction data (addresses, values, gas)            │
│    │   ├── Calculate derived metrics (ETH values, gas prices)           │
│    │   └── Clean and validate data structures                           │
│    │                                                                      │
│    └── LOAD PHASE                                                        │
│        ├── Store block data in PostgreSQL/MongoDB                       │
│        ├── Store transaction data with relationships                     │
│        ├── Handle database errors and rollbacks                         │
│        └── Update collection statistics                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. DATA PROCESSING & ANALYSIS                                            │
│    ├── Pandas Data Processing                                            │
│    │   ├── Load data from databases                                      │
│    │   ├── Perform statistical analysis                                  │
│    │   ├── Calculate transaction patterns                                │
│    │   └── Generate time series metrics                                  │
│    │                                                                      │
│    ├── Real-time Monitoring                                              │
│    │   ├── Track latest block numbers                                    │
│    │   ├── Monitor transaction volumes                                   │
│    │   ├── Calculate gas price trends                                    │
│    │   └── Alert on anomalies                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 6. WEB INTERFACES                                                        │
│    ├── Streamlit Dashboard                                               │
│    │   ├── Real-time blockchain metrics                                 │
│    │   ├── Interactive charts and graphs                                │
│    │   ├── Block explorer functionality                                 │
│    │   └── Transaction search and analysis                              │
│    │                                                                      │
│    ├── FastAPI REST Endpoints                                            │
│    │   ├── GET /blocks - Retrieve block data                            │
│    │   ├── GET /transactions - Get transaction info                     │
│    │   ├── GET /stats - Network statistics                              │
│    │   └── POST /collect - Trigger data collection                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 7. AUTOMATION & SCHEDULING                                               │
│    ├── Schedule Library Integration                                      │
│    │   ├── Periodic data collection (every N minutes)                   │
│    │   ├── Automated ETL pipeline execution                             │
│    │   ├── Error handling and retry logic                               │
│    │   └── Logging and monitoring                                       │
│    │                                                                      │
│    ├── Background Tasks                                                  │
│    │   ├── Continuous blockchain monitoring                              │
│    │   ├── Database maintenance and cleanup                              │
│    │   ├── Performance optimization                                      │
│    │   └── Health checks and alerts                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 8. ERROR HANDLING & LOGGING                                              │
│    ├── Exception Management                                              │
│    │   ├── Network connection errors                                     │
│    │   ├── Database operation failures                                   │
│    │   ├── Rate limiting and API errors                                 │
│    │   └── Data validation errors                                       │
│    │                                                                      │
│    ├── Logging System                                                    │
│    │   ├── Structured logging with levels                               │
│    │   ├── Performance metrics tracking                                  │
│    │   ├── Error reporting and debugging                                 │
│    │   └── Audit trail for data operations                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 9. SHUTDOWN & CLEANUP                                                    │
│    ├── Graceful shutdown procedures                                      │
│    │   ├── Close database connections                                    │
│    │   ├── Stop background tasks                                         │
│    │   ├── Save current state                                            │
│    │   └── Clean up temporary resources                                  │
│    │                                                                      │
│    ├── Data Persistence                                                  │
│    │   ├── Commit pending transactions                                   │
│    │   ├── Update collection statistics                                  │
│    │   ├── Backup critical data                                          │
│    │   └── Log shutdown events                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           APPLICATION END                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### **🔄 Flow Control Points**

- **🟢 Success Path:** Each step continues to the next
- **🟡 Validation Points:** Data integrity checks at each phase
- **🔴 Error Handling:** Automatic retry and fallback mechanisms
- **🔄 Loops:** Continuous monitoring and scheduled tasks
- **📊 Monitoring:** Real-time metrics and health checks

## 🛠️ Tech Stack

### Core Technologies
- **Python 3.8+** - Main programming language
- **Web3.py** - Ethereum blockchain interaction
- **SQLAlchemy** - Database ORM for PostgreSQL
- **PyMongo** - MongoDB driver
- **Streamlit** - Interactive web dashboard
- **FastAPI** - REST API framework for data endpoints
- **Uvicorn** - ASGI server for FastAPI applications

### External Services
- **Infura** - Ethereum node provider
- **PostgreSQL** - Relational database for structured data
- **MongoDB** - NoSQL database for flexible document storage

### Key Libraries
- **pandas** - Data manipulation and analysis for blockchain data processing
- **schedule** - Task scheduling for automated data collection
- **python-dotenv** - Environment variable management for secure configuration
- **requests** - HTTP client for API calls and external service communication
- **Pydantic** - Data validation and settings management

## 📦 Dependencies Explained

### **Blockchain & Web3**
- **web3==6.11.3** - Core Ethereum interaction library
  - Connects to Ethereum network via Infura
  - Retrieves blocks, transactions, and account data
  - Handles Web3 protocol communication
  - Provides utilities for address validation and balance checking

### **Data Processing**
- **pandas==2.1.4** - Data manipulation and analysis
  - Processes large datasets of blockchain data
  - Performs statistical analysis on transaction patterns
  - Handles time series data for blockchain metrics
  - Exports data to various formats (CSV, JSON, etc.)

### **Database Connectivity**
- **psycopg2-binary==2.9.9** - PostgreSQL adapter
  - Connects to PostgreSQL database for structured data storage
  - Handles efficient bulk data insertion
  - Manages database transactions and connections
  - Optimized for high-performance blockchain data storage

- **pymongo==4.6.0** - MongoDB driver
  - Connects to MongoDB for flexible document storage
  - Stores complex blockchain data structures
  - Handles JSON-like data efficiently
  - Provides aggregation capabilities for data analysis

- **sqlalchemy==2.0.23** - Database ORM
  - Object-Relational Mapping for PostgreSQL
  - Defines database models (Block, Transaction)
  - Manages database schema and migrations
  - Provides query interface for data retrieval

### **Web Framework & APIs**
- **streamlit==1.28.2** - Interactive web dashboard
  - Creates real-time blockchain data visualization
  - Provides user-friendly interface for data exploration
  - Displays charts, tables, and interactive components
  - Enables live monitoring of blockchain activity

- **fastapi==0.104.1** - REST API framework
  - Exposes blockchain data via REST endpoints
  - Provides programmatic access to collected data
  - Handles API authentication and rate limiting
  - Generates automatic API documentation

- **uvicorn==0.24.0** - ASGI server
  - Runs FastAPI applications in production
  - Handles concurrent requests efficiently
  - Provides WebSocket support for real-time updates
  - Optimized for high-performance API serving

### **Configuration & Utilities**
- **python-dotenv==1.0.0** - Environment management
  - Loads configuration from .env files
  - Securely manages API keys and database credentials
  - Separates configuration from code
  - Supports different environments (dev, prod, test)

- **requests==2.31.0** - HTTP client
  - Makes API calls to external services
  - Handles HTTP requests and responses
  - Provides session management and retry logic
  - Used for additional blockchain data sources

### **Automation & Scheduling**
- **schedule==1.2.0** - Task scheduling
  - Automates blockchain data collection
  - Runs periodic data collection tasks
  - Manages scheduled ETL pipeline execution
  - Provides cron-like functionality for Python

### **Data Validation**
- **pydantic==2.5.0** - Data validation
  - Validates blockchain data structures
  - Ensures data integrity and type safety
  - Provides automatic data serialization
  - Used for API request/response models

## 📁 Project Structure

```
ETHblockChain/
├── config.py              # Configuration management
├── blockchain_client.py   # Ethereum blockchain interaction
├── database.py            # Database operations (PostgreSQL/MongoDB)
├── etl_pipeline.py        # ETL pipeline implementation
├── dashboard.py           # Streamlit dashboard
├── main.py               # Command-line interface
├── test_connection.py    # Connection testing script
├── test_infura_connection.py  # Infura-specific connection test
├── requirements.txt      # Python dependencies
├── env_example.txt       # Environment variables template
├── .gitignore           # Git ignore patterns
└── README.md            # Project documentation
```

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8 or higher
- MongoDB (optional, for NoSQL storage)
- PostgreSQL (optional, for relational storage)

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd ETHblockChain

# Install dependencies
pip install -r requirements.txt
```

**Note:** The installation includes all necessary dependencies for:
- **Blockchain interaction** (Web3.py)
- **Database operations** (PostgreSQL, MongoDB)
- **Data processing** (Pandas)
- **Web dashboard** (Streamlit)
- **API endpoints** (FastAPI)
- **Automation** (Schedule)

### 3. Configuration

1. **Get Infura API Access (Recommended):**
   - Sign up at [Infura.io](https://infura.io/)
   - Create a new project and get your Project ID
   - The free tier includes 100,000 requests per day

2. **Set up Environment Variables:**
   ```bash
   # Copy the example file
   cp env_example.txt .env
   
   # Edit .env with your Infura credentials
   INFURA_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
   
   # Optional: Alchemy as fallback (not recommended)
   # ALCHEMY_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
   ```

3. **Database Setup (Optional):**
   - **MongoDB:** Install and start MongoDB service
   - **PostgreSQL:** Install PostgreSQL and create a database

### 4. Test Connection

```bash
# Test Infura connection
python test_infura_connection.py

# Test basic blockchain connection
python test_connection.py

# Test full system (requires database)
python main.py test
```

### 5. Start Data Collection

```bash
# Collect latest 10 blocks
python main.py collect --latest 10

# Collect historical blocks
python main.py collect --historical --start 1000 --end 1100

# Run scheduled collection (every 5 minutes)
python main.py collect --scheduled --interval 5
```

### 6. Launch Dashboard

```bash
# Start the interactive dashboard
python main.py dashboard
```

## 📊 Features

### 🔗 Blockchain Integration
- **Real-time Connection:** Connect to Ethereum mainnet via Infura
- **Block Data Extraction:** Retrieve complete block information
- **Transaction Analysis:** Extract detailed transaction data
- **Address Validation:** Validate Ethereum addresses
- **Balance Queries:** Get ETH balances for addresses

### 🗄️ Data Storage
- **Dual Database Support:** PostgreSQL and MongoDB
- **Structured Schema:** Optimized database design for blockchain data
- **Data Integrity:** Automatic data validation and error handling
- **Indexing:** Efficient querying with proper database indexes

### 📈 ETL Pipeline
- **Extract:** Pull data from Ethereum blockchain
- **Transform:** Clean and structure raw blockchain data
- **Load:** Store processed data in databases
- **Scheduling:** Automated data collection at configurable intervals
- **Error Handling:** Robust error handling and logging

### 📊 Visualization Dashboard
- **Real-time Metrics:** Live blockchain statistics
- **Block Explorer:** Search and view block details
- **Transaction Analysis:** Transaction statistics and trends
- **Network Statistics:** Network activity and performance metrics
- **Interactive Charts:** Gas usage, transaction volume, block times

## 🎯 Use Cases

### Data Analytics
- **Network Analysis:** Monitor Ethereum network activity
- **Transaction Patterns:** Analyze transaction behavior and trends
- **Gas Price Analysis:** Track gas price fluctuations
- **Address Monitoring:** Track specific address activity

### Research & Development
- **Academic Research:** Blockchain data for research projects
- **Trading Analysis:** Historical data for trading strategies
- **DApp Development:** Data for decentralized application development
- **Compliance:** Regulatory reporting and compliance monitoring

### Business Intelligence
- **Market Analysis:** Cryptocurrency market insights
- **Risk Assessment:** Blockchain risk analysis
- **Performance Monitoring:** Network performance metrics
- **Competitive Analysis:** Compare with other blockchain networks

## 🔧 Configuration

### Environment Variables
```bash
# Ethereum Configuration
INFURA_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
# Optional: Alchemy as fallback (not recommended)
# ALCHEMY_URL=https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=blockchain_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=blockchain_data

# Data Collection Configuration
BATCH_SIZE=100
START_BLOCK=0
END_BLOCK=0

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=blockchain_collector.log
```

### Database Schema

#### PostgreSQL Tables
```sql
-- Blocks table
CREATE TABLE blocks (
    block_number BIGINT PRIMARY KEY,
    block_hash VARCHAR(66) UNIQUE NOT NULL,
    parent_hash VARCHAR(66) NOT NULL,
    timestamp BIGINT NOT NULL,
    miner VARCHAR(42) NOT NULL,
    difficulty BIGINT NOT NULL,
    gas_limit BIGINT NOT NULL,
    gas_used BIGINT NOT NULL,
    transaction_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE transactions (
    tx_hash VARCHAR(66) PRIMARY KEY,
    block_number BIGINT NOT NULL,
    from_address VARCHAR(42) NOT NULL,
    to_address VARCHAR(42),
    value_wei BIGINT NOT NULL,
    value_ether FLOAT NOT NULL,
    gas BIGINT NOT NULL,
    gas_price BIGINT NOT NULL,
    gas_price_gwei FLOAT NOT NULL,
    input_data TEXT,
    nonce BIGINT NOT NULL,
    transaction_index INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### MongoDB Collections
- **blocks:** Block data with embedded transactions
- **transactions:** Individual transaction records

## 📈 Performance Considerations

### Rate Limiting
- **API Limits:** Respect Infura rate limits (100k requests/day free tier)
- **Batch Processing:** Process blocks in configurable batches
- **Sleep Intervals:** Built-in delays to prevent API throttling

### Database Optimization
- **Indexing:** Proper indexes on frequently queried fields
- **Connection Pooling:** Efficient database connection management
- **Batch Inserts:** Optimized bulk data insertion

### Memory Management
- **Streaming:** Process data in streams to manage memory usage
- **Cleanup:** Automatic cleanup of temporary data structures
- **Monitoring:** Memory usage monitoring and optimization

## 🛡️ Security

### API Security
- **Environment Variables:** Secure storage of API keys
- **HTTPS:** All API communications use HTTPS
- **Rate Limiting:** Built-in rate limiting to prevent abuse

### Data Security
- **Input Validation:** Validate all blockchain data
- **SQL Injection Prevention:** Use parameterized queries
- **Access Control:** Database access control and authentication

## 🐛 Troubleshooting

### Common Issues

1. **Connection Errors:**
   ```bash
   # Test Infura connection specifically
   python test_infura_connection.py
   
   # Check your API key
   python test_connection.py
   ```

2. **Database Connection:**
   ```bash
   # Test database connection
   python main.py test
   ```

3. **Memory Issues:**
   - Reduce batch size in configuration
   - Use smaller block ranges for historical collection

4. **Rate Limiting:**
   - Increase sleep intervals in ETL pipeline
   - Use multiple API providers

### Logging
- **Log Files:** Check `blockchain_collector.log` for detailed error information
- **Log Levels:** Configure log level in environment variables
- **Debug Mode:** Enable debug logging for troubleshooting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Ethereum Foundation** for the blockchain technology
- **Infura** for providing Ethereum node access
- **Web3.py** community for the excellent Python library
- **Streamlit** team for the interactive dashboard framework

## 📞 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

---

**Happy Blockchain Data Collecting! 🚀**