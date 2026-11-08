
import requests
import pandas as pd
import yfinance as yf

def obtener_velas_binance(simbolo="BTCUSDT", intervalo="1h", limite=100):
    """Obtiene datos de velas (OHLCV) desde la API pública de Binance."""
    url = f"https://api.binance.com/api/v3/klines?symbol={simbolo.upper()}&interval={intervalo}&limit={limite}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            # Limpieza y conversión de tipos
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
            # A veces yfinance devuelve multi-index en columnas, lo aplanamos si hace falta
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df.reset_index()
            # Normalizar nombres de columnas
            df.rename(columns={'Datetime': 'timestamp', 'Date': 'timestamp', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'}, inplace=True)
            return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    except Exception as e:
        print(f"Error obteniendo Forex/Activo: {e}")
    return pd.DataFrame()
