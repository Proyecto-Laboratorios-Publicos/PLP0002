import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from api_client import obtener_velas_binance, obtener_datos_forex, obtener_datos_coingecko_global, obtener_pares_binance, obtener_pares_forex
from indicators import calcular_indicadores
from streamlit_autorefresh import st_autorefresh

# Refrescar automáticamente la app cada 5 segundos (5000 ms)
st_autorefresh(interval=5000, limit=None, key="centinela_counter")

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
st.markdown("Centro de comando y vigilancia de mercados en tiempo real. Análisis técnico avanzado y alertas automatizadas.")

# --- BARRA LATERAL (CONTROLES) ---
st.sidebar.header("⚙️ Configuración de Vigilancia")
mercado = st.sidebar.selectbox("Seleccionar Mercado", ["Criptomonedas (Binance)", "Forex / Acciones (yfinance)"])

if mercado == "Criptomonedas (Binance)":
    # Obtenemos la lista dinámica de pares
    with st.spinner("Cargando pares disponibles desde Binance..."):
        lista_pares = obtener_pares_binance()
    
    # Buscamos un índice por defecto razonable (ej: BTCUSDT si existe)
    default_idx = lista_pares.index("BTCUSDT") if "BTCUSDT" in lista_pares else 0
    
    simbolo = st.sidebar.selectbox("Par (Símbolo)", lista_pares, index=default_idx)
    intervalo = st.sidebar.selectbox("Temporalidad", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3)
    limite = st.sidebar.slider("Cantidad de Velas", 50, 500, 150)
    
    with st.spinner(f"Consultando datos de {simbolo} en Binance..."):
        df = obtener_velas_binance(simbolo=simbolo, intervalo=intervalo, limite=limite)
        
    cg_data = obtener_datos_coingecko_global()
    if cg_data:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🌐 Mercado Global (CoinGecko)")
        st.sidebar.metric("Dominancia BTC", f"{cg_data.get('btc_dominance', 0):.1f}%")
        st.sidebar.metric("Dominancia ETH", f"{cg_data.get('eth_dominance', 0):.1f}%")
else:
    # Obtenemos la lista de pares de Forex y activos tradicionales
    lista_forex = obtener_pares_forex()
    default_forex_idx = lista_forex.index("EURUSD=X") if "EURUSD=X" in lista_forex else 0
    
    ticker = st.sidebar.selectbox("Ticker / Par (yfinance)", lista_forex, index=default_forex_idx)
    periodo = st.sidebar.selectbox("Período histórico", ["1d", "5d", "1mo", "6mo", "1y"], index=1)
    intervalo_yf = st.sidebar.selectbox("Intervalo yf", ["1m", "5m", "1h", "1d"], index=2)
    
    with st.spinner(f"Obteniendo cotización de {ticker}..."):
        df = obtener_datos_forex(ticker=ticker, periodo=periodo, intervalo=intervalo_yf)

# --- VALIDACIÓN Y CÁLCULOS TÉCNICOS ---
if df is None or df.empty:
    st.error("⚠️ No se pudieron recuperar datos para este activo en este momento. Prueba seleccionando otra temporalidad o par.")
    st.stop()
else:
    # Aplicar motor de indicadores técnicos avanzados
    df = calcular_indicadores(df)

    if len(df) < 2:
        st.warning("⚠️ El activo seleccionado no devolvió suficientes velas para el intervalo configurado. Prueba ampliando el período o la cantidad de velas.")
        st.stop()

    precio_actual = df['close'].iloc[-1]
    precio_anterior = df['close'].iloc[-2]
    cambio_pct = ((precio_actual - precio_anterior) / precio_anterior) * 100
    max_periodo = df['high'].max()
    min_periodo = df['low'].max()
    volumen_total = df['volume'].sum()
    rsi_actual = df['rsi14'].iloc[-1] if 'rsi14' in df else 50

    # Panel de Métricas Superiores
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Precio Actual", f"${precio_actual:,.2f}", f"{cambio_pct:.2f}%")
    col2.metric("Máximo del Periodo", f"${max_periodo:,.2f}")
    col3.metric("Mínimo del Periodo", f"${min_periodo:,.2f}")
    col4.metric("RSI (14)", f"{rsi_actual:.1f}")

    st.markdown("---")

    # --- GRÁFICO TÉCNICO MULTI-PANE (Velas, EMAs, Bollinger y RSI) ---
    st.subheader("📊 Gráfico Técnico Avanzado (EMAs, Bollinger & RSI)")
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, row_heights=[0.75, 0.25])
    
    # 1. Velas OHLC
    fig.add_trace(go.Candlestick(
        x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'],
        name='OHLC', increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
    ), row=1, col=1)
    
    # 2. EMAs (9 y 21)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['ema9'], name='EMA 9', line=dict(color='#29b6f6', width=1.2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['ema21'], name='EMA 21', line=dict(color='#ffa726', width=1.2)), row=1, col=1)

    # 3. Bandas de Bollinger
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['bollinger_upper'], name='Bollinger Superior', line=dict(color='rgba(255,255,255,0.3)', width=1, dash='dot')), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['bollinger_lower'], name='Bollinger Inferior', line=dict(color='rgba(255,255,255,0.3)', width=1, dash='dot'), fill='tonexty', fillcolor='rgba(255,255,255,0.03)'), row=1, col=1)

    # 4. Panel de RSI inferior
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['rsi14'], name='RSI (14)', line=dict(color='#ab47bc', width=1.5)), row=2, col=1)
    
    # Líneas de referencia para sobrecompra (70) y sobreventa (30)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    fig.update_layout(
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=700,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- MOTOR DE ALERTAS TEMPRANAS AVANZADO ---
    st.markdown("---")
    st.subheader("🚨 Panel de Alertas y Monitoreo Automático")
    
    alertas = []
    if abs(cambio_pct) >= 2.5:
        alertas.append(f"⚠️ **Volatilidad Extrema:** Movimiento de {cambio_pct:.2f}% en la última vela.")
    if rsi_actual >= 70:
        alertas.append(f"🔥 **Sobrecompra (RSI > 70):** El activo marca {rsi_actual:.1f}, posible zona de agotamiento alcista.")
    elif rsi_actual <= 30:
        alertas.append(f"❄️ **Sobreventa (RSI < 30):** El activo marca {rsi_actual:.1f}, posible zona de rebote.")

    if alertas:
        for alerta in alertas:
            st.warning(alerta)
    else:
        st.success("✅ **Sistema en Guardia:** Mercado operando en rangos estables sin alertas críticas de RSI o volatilidad.")
