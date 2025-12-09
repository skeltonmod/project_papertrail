from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import threading
import time
from config import Config
# TODO: Add Binance Adapter
# from adapters.binance_adapter import BinanceAdapter
from adapters.alpaca_adapter import AlpacaAdapter
from strategies.moving_average import MovingAverageCrossover
from services.trading_service import TradingService

# Setup the fucking app
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)


def create_exchange_adapter():
    return AlpacaAdapter(
            api_key=Config.ALPACA_API_KEY,
            api_secret=Config.ALPACA_API_SECRET,
            testnet=Config.USE_TESTNET
        )
    # if Config.EXCHANGE.lower() == 'binance':
    #     return BinanceAdapter(
    #         api_key=Config.BINANCE_API_KEY,
    #         api_secret=Config.BINANCE_API_SECRET,
    #         testnet=Config.USE_TESTNET
    #     )
    # elif Config.EXCHANGE.lower() == 'alpaca':
    #     return AlpacaAdapter(
    #         api_key=Config.ALPACA_API_KEY,
    #         api_secret=Config.ALPACA_API_SECRET,
    #         testnet=Config.USE_TESTNET
    #     )
    # else:
    #     raise ValueError(f"Unsupported exchange: {Config.EXCHANGE}")
    
    
def create_strategy():
    if Config.STRATEGY.lower() == 'moving_average':
        return MovingAverageCrossover(
            symbols=Config.TRADING_SYMBOLS,
            short_window=Config.MA_SHORT_WINDOW,
            long_window=Config.MA_LONG_WINDOW,
            quantity=Config.TRADE_QUANTITY
        )
    else:
        raise ValueError(f"Unsupported strategy: {Config.STRATEGY}")

trading_service = None
trading_thread = None
is_trading = False

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'exchange': Config.EXCHANGE,
        'testnet': Config.USE_TESTNET,
        'strategy': Config.STRATEGY,
        'is_trading': is_trading
    })

@app.route('/api/start', methods=['POST'])
def start_trading():
    """Start the trading bot"""
    global trading_service, trading_thread, is_trading
    
    if is_trading:
        return jsonify({'error': 'Trading already running'}), 400
    
    try:
        # Initialize components
        exchange = create_exchange_adapter()
        strategy = create_strategy()
        trading_service = TradingService(exchange, strategy)
        
        # Start trading loop
        is_trading = True
        trading_thread = threading.Thread(target=trading_loop, daemon=True)
        trading_thread.start()
        
        logger.info("Trading bot started successfully")
        return jsonify({
            'status': 'started',
            'exchange': Config.EXCHANGE,
            'symbols': Config.TRADING_SYMBOLS,
            'strategy': Config.STRATEGY
        })
        
    except Exception as e:
        logger.error(f"Error starting trading: {str(e)}")
        is_trading = False
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_trading():
    global is_trading
    
    if not is_trading:
        return jsonify({'error': 'Trading not running'}), 400
    
    is_trading = False
    logger.info("Trading bot stopped")
    
    return jsonify({'status': 'stopped'})

@app.route('/api/execute', methods=['POST'])
def execute_single():
    global trading_service
    
    if not trading_service:
        exchange = create_exchange_adapter()
        strategy = create_strategy()
        trading_service = TradingService(exchange, strategy)
    
    data = request.get_json()
    symbol = data.get('symbol')
    
    if not symbol:
        return jsonify({'error': 'Symbol is required'}), 400
    
    try:
        result = trading_service.execute_strategy(symbol)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error executing strategy: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/account', methods=['GET'])
def get_account():
    global trading_service
    
    if not trading_service:
        exchange = create_exchange_adapter()
        strategy = create_strategy()
        trading_service = TradingService(exchange, strategy)
    
    try:
        account_info = trading_service.get_account_info()
        return jsonify(account_info)
    except Exception as e:
        logger.error(f"Error getting account info: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/positions', methods=['GET'])
def get_positions():
    global trading_service
    
    if not trading_service:
        return jsonify({'positions': {}})
    
    positions = trading_service.get_positions()
    return jsonify({'positions': positions})

@app.route('/api/history', methods=['GET'])
def get_history():
    global trading_service
    
    if not trading_service:
        return jsonify({'history': []})
    
    history = trading_service.get_trade_history()
    return jsonify({'history': history})

@app.route('/api/price/<symbol>', methods=['GET'])
def get_price(symbol):
    """Get current price for a symbol"""
    try:
        exchange = create_exchange_adapter()
        price = exchange.get_price(symbol)
        return jsonify({
            'symbol': symbol,
            'price': price
        })
    except Exception as e:
        logger.error(f"Error getting price: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info(f"Starting Flask app on {Config.HOST}:{Config.PORT}")
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )