# 🚀 Infura Setup Guide

This guide will help you configure your Ethereum blockchain project to use Infura as the primary Ethereum node provider.

## 📋 Prerequisites

- Python 3.8 or higher installed
- An Infura account (free at [infura.io](https://infura.io/))

## 🔑 Step 1: Get Your Infura Project ID

1. **Sign up/Login to Infura:**
   - Go to [https://infura.io/](https://infura.io/)
   - Create an account or log in to your existing account

2. **Create a New Project:**
   - Click "Create New Project"
   - Select "Web3 API" as the project type
   - Give your project a name (e.g., "Blockchain Data Collector")
   - Click "Create"

3. **Get Your Project ID:**
   - In your project dashboard, you'll see your Project ID
   - It looks like: `1234567890abcdef1234567890abcdef`
   - Copy this Project ID - you'll need it for the next step

## ⚙️ Step 2: Configure Your Environment

1. **Create Environment File:**
   ```bash
   # Copy the example file
   cp env_example.txt .env
   ```

2. **Edit the .env file:**
   ```bash
   # Open .env in your preferred editor
   # Replace YOUR_PROJECT_ID with your actual Infura Project ID
   
   INFURA_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
   ```

   **Example:**
   ```bash
   INFURA_URL=https://mainnet.infura.io/v3/1234567890abcdef1234567890abcdef
   ```

## 🧪 Step 3: Test Your Connection

1. **Run the Infura Test:**
   ```bash
   python test_infura_connection.py
   ```

2. **Expected Output:**
   ```
   🧪 Testing Infura Connection...
   ==================================================
   🔗 Testing connection to: https://mainnet.infura.io/v3/YOUR_PROJECT_ID
   ✅ Successfully connected to Ethereum network
   📦 Latest block number: 12345678
   ✅ Successfully retrieved block 12345677
   📊 Block has 150 transactions
   ✅ Successfully retrieved transaction details
   🔗 Transaction hash: 0x1234567890abcdef...
   💰 Value: 0.5 ETH
   
   🎉 All tests passed! Infura connection is working properly.
   
   ✅ Ready to use Infura for your Ethereum blockchain project!
   ```

## 🚀 Step 4: Start Using Your Project

Once the connection test passes, you can:

1. **Test the full system:**
   ```bash
   python main.py test
   ```

2. **Start collecting data:**
   ```bash
   # Collect latest 10 blocks
   python main.py collect --latest 10
   
   # Collect historical blocks
   python main.py collect --historical --start 1000 --end 1100
   ```

3. **Launch the dashboard:**
   ```bash
   python main.py dashboard
   ```

## 🔧 Troubleshooting

### ❌ "INFURA_URL not set or still using placeholder value"
**Solution:** Make sure you've:
- Created the `.env` file from `env_example.txt`
- Replaced `YOUR_PROJECT_ID` with your actual Infura Project ID
- Saved the file

### ❌ "Error connecting to Ethereum network"
**Possible causes:**
- Invalid Project ID
- Network connectivity issues
- Infura service temporarily down

**Solutions:**
- Double-check your Project ID in the Infura dashboard
- Verify your internet connection
- Check [Infura Status](https://status.infura.io/) for service issues

### ❌ "Rate limit exceeded"
**Solution:** 
- The free tier includes 100,000 requests per day
- Consider upgrading to a paid plan for higher limits
- Implement longer delays between requests in your code

## 📊 Infura Free Tier Limits

- **100,000 requests per day**
- **25 requests per second**
- **Archive data access** (limited)
- **WebSocket connections** (limited)

For higher limits, consider upgrading to a paid plan.

## 🔒 Security Best Practices

1. **Never commit your .env file:**
   ```bash
   # Make sure .env is in your .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use environment variables in production:**
   ```bash
   export INFURA_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
   ```

3. **Rotate your Project ID regularly** for enhanced security

## 📞 Support

- **Infura Documentation:** [https://docs.infura.io/](https://docs.infura.io/)
- **Infura Support:** [https://support.infura.io/](https://support.infura.io/)
- **Project Issues:** Create an issue in this repository

---

**Happy Blockchain Data Collecting! 🚀** 