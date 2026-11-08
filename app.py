import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from api_client import obtener_velas_binance, obtener_datos_forex, obtener_datos_coingecko_global

# Configuración inicial de la página
st.set_page_config(
    page_title="Crypto & Forex Sentinel",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 8px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ Crypto & Forex Sentinel")
st.markdown("Centro de comando y vigilancia de mercados en tiempo real. Análisis técnico y alertas automatizadas sin riesgo.")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("⚙️ Configuración de Vigilancia")
mercado = st.sidebar.selectbox("Seleccionar Mercado", ["Criptomonedas (Binance)", "Forex / Acciones (yfinance)"])

if mercado == "Criptomonedas (Binance)":
    simbolo = st.sidebar.text_input("Par (Símbolo)", value="BTCUSDT").upper()
    intervalo = st.sidebar.selectbox("Temporalidad", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3)
    limite = st.sidebar.slider("Cantidad de Velas", 50, 500, 150)
    
    with st.spinner("Consultando datos de Binance..."):
        df = obtener_velas_binance(simbolo=simbolo, intervalo=intervalo, limite=limite)
        
    # Datos globales de CoinGecko en el sidebar o expander
    cg_data = obtener_datos_coingecko_global()
    if cg_data:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🌐 Mercado Global (CoinGecko)")
        st.sidebar.metric("Dominancia BTC", f"{cg_data.get('btc_dominance', 0):.1f}%")
        st.sidebar.metric("Dominancia ETH", f"{cg_data.get('eth_dominance', 0):.1f}%")
else:
    ticker = st.sidebar.text_input("Ticker (Ej: EURUSD=X, AAPL, GC=F)", value="EURUSD=X").upper()
    periodo = st.sidebar.selectbox("Período histórico", ["1d", "5d", "1mo", "6mo", "1y"], index=1)
    intervalo_yf = st.sidebar.selectbox("Intervalo yf", ["1m", "5m", "1h", "1d"], index=2)
    
    with st.spinner(f"Obteniendo cotización de {ticker}..."):
        df = obtener_datos_forex(ticker=ticker, periodo=periodo, intervalo=intervalo_yf)

# --- VALIDACIÓN Y CÁLCULOS TÉCNICOS ---
if df.empty:
    st.error("⚠️ No se pudieron recuperar datos con los parámetros seleccionados.")
else:
    # Indicadores técnicos sencillos (SMA 20)
    df['sma20'] = df['close'].rolling(window=20).mean()

    precio_actual = df['close'].iloc[-1]
    precio_anterior = df['close'].iloc[-2]
    cambio_pct = ((precio_actual - precio_anterior) / precio_anterior) * 100
    max_periodo = df['high'].max()
    min_periodo = df['low'].min()
    volumen_total = df['volume'].sum()

    # Panel de Métricas Superiores
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Precio Actual", f"${precio_actual:,.2f}", f"{cambio_pct:.2f}%")
    col2.metric("Máximo del Periodo", f"${max_periodo:,.2f}")
    col3.metric("Mínimo del Periodo", f"${min_periodo:,.2f}")
    col4.metric("Volumen Operado", f"{volumen_total:,.0f}")

    st.markdown("---")

    # --- GRÁFICO DE VELAS CON SMA ---
    st.subheader("📊 Gráfico de Velas y Media Móvil (SMA 20)")
    
    fig = go.Figure()
    
    # Velas
    fig.add_trace(go.Candlestick(
        x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'],
        name='OHLC', increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
    ))
    
    # Línea SMA 20
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['sma20'], name='SMA 20', line=f"color='orange', width=1.5"
    )) if 'sma20' in df else None

    fig.update_layout(
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=550,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- MOTOR DE ALERTAS TEMPRANAS ---
    st.markdown("---")
    st.subheader("🚨 Panel de Alertas y Monitoreo Automático")
    
    umbral_volatilidad = 2.5
    if abs(cambio_pct) >= umbral_volatilidad:
        st.warning(f"⚠️ **ALERTA DE VOLATILIDAD:** Movimiento brusco detectado de {cambio_pct:.2f}% en el último bloque.")
    else:
        st.success("✅ **Sistema en Guardia:** Mercado operando dentro de rangos normales de volatilidad.")
