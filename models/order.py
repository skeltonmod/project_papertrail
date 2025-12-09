from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Order:
    """Trading order data model"""
    order_id: str
    symbol: str
    side: str  # 'BUY' or 'SELL'
    type: str  # 'MARKET', 'LIMIT', etc.
    quantity: float
    filled_quantity: float
    price: float  # 0 for market orders, limit price for limit orders
    status: str  # 'NEW', 'FILLED', 'CANCELLED', etc.
    timestamp: int  # Unix timestamp in milliseconds
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Order':
        """Create Order from dictionary"""
        return cls(**data)
    
    def to_dict(self) -> dict:
        """Convert Order to dictionary"""
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side,
            'type': self.type,
            'quantity': self.quantity,
            'filled_quantity': self.filled_quantity,
            'price': self.price,
            'status': self.status,
            'timestamp': self.timestamp
        }
    
    def is_filled(self) -> bool:
        """Check if order is completely filled"""
        return self.status == 'FILLED' or self.filled_quantity >= self.quantity
    
    def get_datetime(self) -> datetime:
        """Get timestamp as datetime object"""
        return datetime.fromtimestamp(self.timestamp / 1000)