# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Exchange settings
    EXCHANGE = os.getenv('EXCHANGE', 'binance')  # 'binance' or 'alpaca'
    USE_TESTNET = os.getenv('USE_TESTNET', 'True').lower() == 'true'
    
    # Binance API credentials
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY', '')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET', '')
    
    # Alpaca API credentials
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', '')
    ALPACA_API_SECRET = os.getenv('ALPACA_API_SECRET', '')
    
    # Trading settings
    TRADING_SYMBOLS = os.getenv('TRADING_SYMBOLS', 'BTCUSDT,ETHUSDT').split(',')
    STRATEGY = os.getenv('STRATEGY', 'moving_average')
    
    # Strategy parameters
    MA_SHORT_WINDOW = int(os.getenv('MA_SHORT_WINDOW', 10))
    MA_LONG_WINDOW = int(os.getenv('MA_LONG_WINDOW', 30))
    TRADE_QUANTITY = float(os.getenv('TRADE_QUANTITY', 0.01))
    
    # Bot settings
    TRADING_INTERVAL = int(os.getenv('TRADING_INTERVAL', 300))  # seconds
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
