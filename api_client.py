import requests
import pandas as pd
import yfinance as yf
import streamlit as st

@st.cache_data(ttl=300)  # Caché de 5 minutos para no saturar CoinGecko
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

@st.cache_data(ttl=600)  # Caché de 10 minutos para la lista de pares de Binance
def obtener_pares_binance():
    """Obtiene la lista oficial de pares de criptomonedas activos en Binance (ej: USDT)."""
    url = "https://data-api.binance.vision/api/v3/exchangeInfo"
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

def obtener_velas_binance(simbolo="BTCUSDT", intervalo="1h", limite=100):
    """Obtiene datos de velas (OHLCV) desde la API pública de Binance usando el endpoint de datos."""
    url = "https://data-api.binance.vision/api/v3/klines"
    params = {
        "symbol": simbolo.strip().upper(),
        "interval": intervalo.strip(),
        "limit": int(limite)
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
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
        else:
            print(f"Binance API Error Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Excepción conectando a Binance: {e}")
        
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

def obtener_pares_forex():
    """Retorna una lista de tickers populares de Forex, Índices y Commodities para yfinance."""
    return [
        "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", 
        "NZDUSD=X", "USDCHF=X", "EURJPY=X", "GBPJPY=X", "EURGBP=X",
        "GC=F", "SI=F", "CL=F", "BTC-USD", "ETH-USD",
        "^IXIC", "^DJI", "^GSPC", "AAPL", "MSFT", "TSLA", "NVDA", "AMZN"
    ]
