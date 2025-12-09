from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime

class BaseExchangeAdapter(ABC):
    """Abstract base class for exchange adapters"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
    
    @abstractmethod
    def get_balance(self, asset: str = None) -> Dict:
        """Get account balance"""
        pass
    
    @abstractmethod
    def get_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        pass
    
    @abstractmethod
    def get_historical_data(self, symbol: str, interval: str, 
                           start_time: datetime, end_time: datetime = None) -> List[Dict]:
        """Get historical OHLCV data"""
        pass
    
    @abstractmethod
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict:
        """Place a market order"""
        pass
    
    @abstractmethod
    def place_limit_order(self, symbol: str, side: str, 
                         quantity: float, price: float) -> Dict:
        """Place a limit order"""
        pass
    
    @abstractmethod
    def cancel_order(self, symbol: str, order_id: str) -> Dict:
        """Cancel an order"""
        pass
    
    @abstractmethod
    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        """Get all open orders"""
        pass
    
    @abstractmethod
    def get_order_status(self, symbol: str, order_id: str) -> Dict:
        """Get order status"""
        pass