from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime

class BaseStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    def __init__(self, name: str, symbols: List[str], params: Dict = None):
        self.name = name
        self.symbols = symbols
        self.params = params or {}
        self.positions = {}
    
    @abstractmethod
    def analyze(self, symbol: str, historical_data: List[Dict], 
                current_price: float) -> Dict:
        """
        Analyze market data and return trading signal
        
        Returns:
            Dict with keys:
                - action: 'BUY', 'SELL', or 'HOLD'
                - quantity: amount to trade (if applicable)
                - confidence: 0-1 confidence score
                - reason: explanation of the signal
        """
        pass
    
    @abstractmethod
    def get_required_history(self) -> str:
        """Return the required historical data period (e.g., '30d', '7d')"""
        pass
    
    @abstractmethod
    def get_required_interval(self) -> str:
        """Return the required data interval (e.g., '1m', '5m', '1h', '1d')"""
        pass
    
    def on_order_filled(self, order: Dict):
        """Callback when an order is filled"""
        symbol = order['symbol']
        if order['side'] == 'BUY':
            self.positions[symbol] = {
                'quantity': order['filled_quantity'],
                'entry_price': order['price'],
                'timestamp': order['timestamp']
            }
        elif order['side'] == 'SELL' and symbol in self.positions:
            del self.positions[symbol]
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get current position for a symbol"""
        return self.positions.get(symbol)