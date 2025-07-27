import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ethereum Configuration
INFURA_URL = os.getenv('INFURA_URL', 'https://mainnet.infura.io/v3/YOUR_PROJECT_ID')

# Database Configuration
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'blockchain_data')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB = os.getenv('MONGODB_DB', 'blockchain_data')

# Data Collection Configuration
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '100'))  # Number of blocks to process in one batch
START_BLOCK = int(os.getenv('START_BLOCK', '0'))  # Starting block number
END_BLOCK = int(os.getenv('END_BLOCK', '0'))      # 0 means latest block

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'blockchain_collector.log') 