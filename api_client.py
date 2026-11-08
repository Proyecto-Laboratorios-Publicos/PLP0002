import requests
import pandas as pd
import yfinance as yf

def obtener_velas_binance(simbolo="BTCUSDT", intervalo="1h", limite=100):
    """Obtiene datos de velas (OHLCV) desde la API pública de Binance."""
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": simbolo.upper(),
        "interval": intervalo,
        "limit": limite
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if not isinstance(data, list) or len(data) == 0:
                return pd.DataFrame()
            
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
                
            return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    except Exception as e:
        print(f"Error conectando a Binance: {e}")
    return pd.DataFrame()

def obtener_datos_forex(ticker="EURUSD=X", periodo="5d", intervalo="1h"):
    """Obtiene datos de Forex o activos tradicionales utilizando yfinance."""
    try:
        df = yf.download(ticker, period=periodo, interval=intervalo, progress=False)
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.reset_index()
            df.rename(columns={'Datetime': 'timestamp', 'Date': 'timestamp', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'}, inplace=True)
            return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    except Exception as e:
        print(f"Error obteniendo Forex/Activo: {e}")
    return pd.DataFrame()

def obtener_datos_coingecko_global():
    """Obtiene métricas globales del mercado cripto desde CoinGecko."""
    url = "https://api.coingecko.com/api/v3/global"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json().get("data", {})
            return {
                "active_cryptos": data.get("active_cryptocurrencies", 0),
                "btc_dominance": data.get("market_cap_percentage", {}).get("btc", 0),
                "eth_dominance": data.get("market_cap_percentage", {}).get("eth", 0),
                "market_cap_change": data.get("market_cap_change_percentage_24h_usd", 0)
            }
    except Exception as e:
        print(f"Error conectando a CoinGecko: {e}")
    return {}

def obtener_pares_binance():
    """Obtiene la lista de pares de criptomonedas activos en Binance (ej: USDT)."""
    url = "https://api.binance.com/api/v3/exchangeInfo"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            pares = [
                s['symbol'] for s in data.get('symbols', []) 
                if s['quoteAsset'] == 'USDT' and s['status'] == 'TRADING'
            ]
            return sorted(pares)
    except Exception as e:
        print(f"Error obteniendo pares de Binance: {e}")
    return ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT", "XRPUSDT"]
