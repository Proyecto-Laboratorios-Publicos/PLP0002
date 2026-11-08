import pandas as pd

def calcular_indicadores(df):
    """Calcula EMAs, Bandas de Bollinger y RSI sobre el DataFrame de precios."""
    if df.empty or 'close' not in df.columns:
        return df

    # 1. Medias Móviles Exponenciales (EMAs)
    df['ema9'] = df['close'].ewm(span=9, adjust=False).mean()
    df['ema21'] = df['close'].ewm(span=21, adjust=False).mean()

    # 2. Bandas de Bollinger (SMA 20 + Desviación Estándar)
    window = 20
    sma20 = df['close'].rolling(window=window).mean()
    std20 = df['close'].rolling(window=window).std()
    df['bollinger_mid'] = sma20
    df['bollinger_upper'] = sma20 + (std20 * 2)
    df['bollinger_lower'] = sma20 - (std20 * 2)

    # 3. RSI (Relative Strength Index - 14 períodos)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    
    # Evitar división por cero
    rs = gain / loss
    df['rsi14'] = 100 - (100 / (1 + rs))

    return df
