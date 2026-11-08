# 🛡️ Crypto & Forex Sentinel

Centro de comando y vigilancia de mercados globales en tiempo real. Diseñado para el análisis técnico avanzado, monitoreo multi-mercado y automatización de alertas operativas.

---

## 🚀 Stack Tecnológico
* **Lenguaje:** Python
* **Interfaz de Usuario:** Streamlit (Optimizado con diseño responsivo y modo oscuro)
* **Visualización de Datos:** Plotly (Gráficos multi-pane interactivos de alta performance)
* **Manipulación de Datos:** Pandas
* **APIs & Fuentes de Datos:** Binance Vision API, Yahoo Finance (`yfinance`) y CoinGecko Global API.

---

## ⚙️ Características Clave
* **Arquitectura Multi-Mercado:** Soporte híbrido para criptomonedas (activos 24/7) y mercados tradicionales (Forex, Commodities e Índices) con validación automática del estado operativo de la bolsa.
* **Indicadores Técnicos en Vivo:** Cálculo dinámico de Medias Móviles Exponenciales (**EMA 9 / EMA 21**), **Bandas de Bollinger** y el Índice de Fuerza Relativa (**RSI 14**).
* **Optimización de Rendimiento:** Implementación de caché nativa (`st.cache_data`) para mitigar la latencia de red y estabilizar la interfaz durante los ciclos de refresco automático.
* **Motor Autónomo (Time-Trading):** Ciclos de sincronización en tiempo real con sellos de tiempo dinámicos y paneles de control resilientes.
