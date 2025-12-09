from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Position:
    """Position tracking data model"""
    symbol: str
    quantity: float
    entry_price: float
    timestamp: int  # Unix timestamp in milliseconds when position was opened
    
    @classmethod
    def from_dict(cls, symbol: str, data: dict) -> 'Position':
        """Create Position from dictionary"""
        return cls(
            symbol=symbol,
            quantity=data['quantity'],
            entry_price=data['entry_price'],
            timestamp=data['timestamp']
        )
    
    def to_dict(self) -> dict:
        """Convert Position to dictionary"""
        return {
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'timestamp': self.timestamp
        }
    
    def get_datetime(self) -> datetime:
        """Get timestamp as datetime object"""
        return datetime.fromtimestamp(self.timestamp / 1000)
    
    def calculate_pnl(self, current_price: float) -> float:
        """Calculate unrealized profit/loss"""
        return (current_price - self.entry_price) * self.quantity
    
    def calculate_pnl_percentage(self, current_price: float) -> float:
        """Calculate unrealized profit/loss as percentage"""
        return ((current_price - self.entry_price) / self.entry_price) * 100