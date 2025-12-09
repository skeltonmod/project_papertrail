from typing import Dict, List, Optional
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from .base_adapter import BaseExchangeAdapter

class AlpacaAdapter(BaseExchangeAdapter):
    """Alpaca stocks trading adapter implementation"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        super().__init__(api_key, api_secret, testnet)
        self.trading_client = TradingClient(api_key, api_secret, paper=testnet)
        self.data_client = StockHistoricalDataClient(api_key, api_secret)
    
    def get_balance(self, asset: str = None) -> Dict:
        """Get account balance"""
        account = self.trading_client.get_account()
        
        if asset:
            positions = self.trading_client.get_all_positions()
            for pos in positions:
                if pos.symbol == asset:
                    return {
                        'asset': pos.symbol,
                        'free': float(pos.qty_available),
                        'locked': float(pos.qty) - float(pos.qty_available),
                        'total': float(pos.qty)
                    }
            return None
        
        return {
            'cash': float(account.cash),
            'portfolio_value': float(account.portfolio_value),
            'buying_power': float(account.buying_power)
        }
    
    def get_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            trades = self.data_client.get_stock_latest_trade({symbol: symbol})
            return float(trades[symbol].price)
        except Exception as e:
            raise Exception(f"Alpaca API error: {str(e)}")
    
    def get_historical_data(self, symbol: str, interval: str,
                           start_time: datetime, end_time: datetime = None) -> List[Dict]:
        """Get historical OHLCV data"""
        # Map interval to Alpaca TimeFrame
        timeframe_map = {
            '1m': TimeFrame.Minute,
            '5m': TimeFrame(5, TimeFrame.Minute),
            '15m': TimeFrame(15, TimeFrame.Minute),
            '1h': TimeFrame.Hour,
            '1d': TimeFrame.Day
        }
        
        timeframe = timeframe_map.get(interval, TimeFrame.Day)
        
        request_params = StockBarsRequest(
            symbol_or_symbols=[symbol],
            timeframe=timeframe,
            start=start_time,
            end=end_time
        )
        
        bars = self.data_client.get_stock_bars(request_params)
        
        return [{
            'timestamp': int(bar.timestamp.timestamp() * 1000),
            'open': float(bar.open),
            'high': float(bar.high),
            'low': float(bar.low),
            'close': float(bar.close),
            'volume': float(bar.volume)
        } for bar in bars[symbol]]
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict:
        """Place a market order"""
        order_side = OrderSide.BUY if side.upper() == 'BUY' else OrderSide.SELL
        
        order_data = MarketOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=order_side,
            time_in_force=TimeInForce.DAY
        )
        
        order = self.trading_client.submit_order(order_data)
        return self._normalize_order(order)
    
    def place_limit_order(self, symbol: str, side: str, 
                         quantity: float, price: float) -> Dict:
        """Place a limit order"""
        order_side = OrderSide.BUY if side.upper() == 'BUY' else OrderSide.SELL
        
        order_data = LimitOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=order_side,
            time_in_force=TimeInForce.DAY,
            limit_price=price
        )
        
        order = self.trading_client.submit_order(order_data)
        return self._normalize_order(order)
    
    def cancel_order(self, symbol: str, order_id: str) -> Dict:
        """Cancel an order"""
        self.trading_client.cancel_order_by_id(order_id)
        return {'order_id': order_id, 'status': 'CANCELLED'}
    
    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        """Get all open orders"""
        orders = self.trading_client.get_orders()
        
        if symbol:
            orders = [o for o in orders if o.symbol == symbol]
        
        return [self._normalize_order(order) for order in orders]
    
    def get_order_status(self, symbol: str, order_id: str) -> Dict:
        """Get order status"""
        order = self.trading_client.get_order_by_id(order_id)
        return self._normalize_order(order)
    
    def _normalize_order(self, order) -> Dict:
        """Normalize order data to standard format"""
        return {
            'order_id': str(order.id),
            'symbol': order.symbol,
            'side': order.side.value,
            'type': order.order_type.value,
            'quantity': float(order.qty),
            'filled_quantity': float(order.filled_qty or 0),
            'price': float(order.limit_price) if order.limit_price else 0,
            'status': order.status.value,
            'timestamp': int(order.created_at.timestamp() * 1000)
        }