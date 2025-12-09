from typing import Dict, List
from .base_strategy import BaseStrategy

class MovingAverageCrossover(BaseStrategy):
    """Simple Moving Average Crossover Strategy"""
    
    def __init__(self, symbols: List[str], short_window: int = 10, 
                 long_window: int = 30, quantity: float = 0.01):
        params = {
            'short_window': short_window,
            'long_window': long_window,
            'quantity': quantity
        }
        super().__init__('MA_Crossover', symbols, params)
        self.short_window = short_window
        self.long_window = long_window
        self.quantity = quantity
    
    def analyze(self, symbol: str, historical_data: List[Dict], 
                current_price: float) -> Dict:
        """Analyze using moving average crossover"""
        
        if len(historical_data) < self.long_window:
            return {
                'action': 'HOLD',
                'quantity': 0,
                'confidence': 0,
                'reason': 'Insufficient data'
            }
        
        # Calculate moving averages
        closes = [candle['close'] for candle in historical_data]
        
        short_ma = sum(closes[-self.short_window:]) / self.short_window
        long_ma = sum(closes[-self.long_window:]) / self.long_window
        
        # Previous MAs for crossover detection
        prev_short_ma = sum(closes[-(self.short_window+1):-1]) / self.short_window
        prev_long_ma = sum(closes[-(self.long_window+1):-1]) / self.long_window
        
        position = self.get_position(symbol)
        
        # Detect crossover
        if short_ma > long_ma and prev_short_ma <= prev_long_ma:
            # Bullish crossover - buy signal
            if not position:
                return {
                    'action': 'BUY',
                    'quantity': self.quantity,
                    'confidence': 0.7,
                    'reason': f'Bullish crossover: SMA({self.short_window})={short_ma:.2f} crossed above SMA({self.long_window})={long_ma:.2f}'
                }
        
        elif short_ma < long_ma and prev_short_ma >= prev_long_ma:
            # Bearish crossover - sell signal
            if position:
                return {
                    'action': 'SELL',
                    'quantity': position['quantity'],
                    'confidence': 0.7,
                    'reason': f'Bearish crossover: SMA({self.short_window})={short_ma:.2f} crossed below SMA({self.long_window})={long_ma:.2f}'
                }
        
        return {
            'action': 'HOLD',
            'quantity': 0,
            'confidence': 0.5,
            'reason': f'No crossover detected. SMA({self.short_window})={short_ma:.2f}, SMA({self.long_window})={long_ma:.2f}'
        }
    
    def get_required_history(self) -> str:
        """Need enough data for long MA plus buffer"""
        days = (self.long_window * 2) // 24  # Assuming hourly data
        return f'{max(days, 7)}d'
    
    def get_required_interval(self) -> str:
        """Use 1 hour intervals"""
        return '1h'