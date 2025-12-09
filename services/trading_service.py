from typing import Dict, List
from datetime import datetime, timedelta
import logging
from adapters.base_adapter import BaseExchangeAdapter
from strategies.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)

class TradingService:
    """Core trading service that coordinates strategies and exchanges"""
    
    def __init__(self, exchange: BaseExchangeAdapter, strategy: BaseStrategy):
        self.exchange = exchange
        self.strategy = strategy
        self.is_running = False
        self.trade_history = []
    
    def execute_strategy(self, symbol: str) -> Dict:
        """Execute strategy for a given symbol"""
        try:
            # Get current price
            current_price = self.exchange.get_price(symbol)
            
            # Get historical data
            interval = self.strategy.get_required_interval()
            history_period = self.strategy.get_required_history()
            
            # Parse history period (e.g., '7d' -> 7 days)
            days = int(history_period.replace('d', ''))
            start_time = datetime.now() - timedelta(days=days)
            
            historical_data = self.exchange.get_historical_data(
                symbol=symbol,
                interval=interval,
                start_time=start_time
            )
            
            # Analyze market
            signal = self.strategy.analyze(symbol, historical_data, current_price)
            
            logger.info(f"{symbol}: {signal['action']} - {signal['reason']}")
            
            # Execute trades based on signal
            if signal['action'] == 'BUY' and signal['quantity'] > 0:
                return self._execute_buy(symbol, signal)
            elif signal['action'] == 'SELL' and signal['quantity'] > 0:
                return self._execute_sell(symbol, signal)
            
            return {
                'status': 'NO_ACTION',
                'symbol': symbol,
                'signal': signal
            }
            
        except Exception as e:
            logger.error(f"Error executing strategy for {symbol}: {str(e)}")
            return {
                'status': 'ERROR',
                'symbol': symbol,
                'error': str(e)
            }
    
    def _execute_buy(self, symbol: str, signal: Dict) -> Dict:
        """Execute buy order"""
        try:
            # Check balance before buying
            balance = self.exchange.get_balance()
            logger.info(f"Executing BUY order for {symbol}: {signal['quantity']} units")
            
            order = self.exchange.place_market_order(
                symbol=symbol,
                side='BUY',
                quantity=signal['quantity']
            )
            
            # Update strategy position
            self.strategy.on_order_filled(order)
            
            # Log trade
            self._log_trade(order, signal)
            
            return {
                'status': 'SUCCESS',
                'action': 'BUY',
                'order': order,
                'signal': signal
            }
            
        except Exception as e:
            logger.error(f"Error executing buy order: {str(e)}")
            return {
                'status': 'ERROR',
                'action': 'BUY',
                'error': str(e)
            }
    
    def _execute_sell(self, symbol: str, signal: Dict) -> Dict:
        """Execute sell order"""
        try:
            logger.info(f"Executing SELL order for {symbol}: {signal['quantity']} units")
            
            order = self.exchange.place_market_order(
                symbol=symbol,
                side='SELL',
                quantity=signal['quantity']
            )
            
            # Update strategy position
            self.strategy.on_order_filled(order)
            
            # Log trade
            self._log_trade(order, signal)
            
            return {
                'status': 'SUCCESS',
                'action': 'SELL',
                'order': order,
                'signal': signal
            }
            
        except Exception as e:
            logger.error(f"Error executing sell order: {str(e)}")
            return {
                'status': 'ERROR',
                'action': 'SELL',
                'error': str(e)
            }
    
    def _log_trade(self, order: Dict, signal: Dict):
        """Log trade to history"""
        trade_log = {
            'timestamp': datetime.now().isoformat(),
            'order': order,
            'signal': signal
        }
        self.trade_history.append(trade_log)
    
    def get_trade_history(self) -> List[Dict]:
        """Get trade history"""
        return self.trade_history
    
    def get_positions(self) -> Dict:
        """Get current positions"""
        return self.strategy.positions
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        try:
            balance = self.exchange.get_balance()
            positions = self.get_positions()
            
            return {
                'balance': balance,
                'positions': positions,
                'open_orders': self.exchange.get_open_orders()
            }
        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
            return {'error': str(e)}