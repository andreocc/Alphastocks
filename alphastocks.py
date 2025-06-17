import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="AlphaStock v1", layout="wide", initial_sidebar_state="expanded")

# Estilo customizado para cards
st.markdown(
    """
    <style>
    .card {
        background-color: #1a1a1a;
        padding: 20px;
        border-radius: 10px;
        color: #ecf0f1;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .card h3 {
        color: #2ecc71;
        margin-bottom: 10px;
    }
    .metric {
        font-size: 24px;
        font-weight: bold;
    }
    .recommendation-buy {
        color: #2ecc71;
        font-weight: 700;
    }
    .recommendation-sell {
        color: #e74c3c;
        font-weight: 700;
    }
    .recommendation-hold {
        color: #f1c40f;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 AlphaAnalytics Pro")

ticker_input = st.text_input("Digite o ticker da ação (ex: PETR4.SA):").upper()

def calcular_indicadores(df):
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    df['SMA50'] = df['Close'].rolling(window=50).mean()
    delta = df['Close'].diff()
    ganho = delta.where(delta > 0, 0)
    perda = -delta.where(delta < 0, 0)
    avg_gain = ganho.rolling(14).mean()
    avg_loss = perda.rolling(14).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df.dropna()

def gerar_recomendacao(row):
    if row['RSI'] < 30 and row['Close'] > row['SMA50']:
        return "COMPRA FORTE 🔺", "recommendation-buy"
    elif row['RSI'] > 70 and row['Close'] < row['SMA50']:
        return "VENDA FORTE 🔻", "recommendation-sell"
    else:
        return "MANTER ⏸️", "recommendation-hold"

if ticker_input:
    try:
        acao = yf.Ticker(ticker_input)
        df = acao.history(period="1y")

        if df.empty:
            st.error("Ticker inválido ou sem dados disponíveis.")
        else:
            df = calcular_indicadores(df)
            ultimo = df.iloc[-1]
            info = acao.info

            # Cards com métricas
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                st.markdown(f'<div class="card"><h3>Preço Atual</h3><div class="metric">R$ {ultimo["Close"]:.2f}</div></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="card"><h3>Média 50 dias</h3><div class="metric">R$ {ultimo["SMA50"]:.2f}</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="card"><h3>RSI</h3><div class="metric">{ultimo["RSI"]:.1f}</div></div>', unsafe_allow_html=True)
            with col4:
                volume_m = ultimo["Volume"] / 1e6
                st.markdown(f'<div class="card"><h3>Volume</h3><div class="metric">{volume_m:.1f}M</div></div>', unsafe_allow_html=True)
            with col5:
                dividendo = info.get('dividendYield', 0)
                st.markdown(f'<div class="card"><h3>Dividendo</h3><div class="metric">{dividendo*100:.2f}%</div></div>', unsafe_allow_html=True)

            # Recomendação
            recomendacao, classe = gerar_recomendacao(ultimo)
            st.markdown(f'<div class="card"><h3>Recomendação</h3><div class="{classe}">{recomendacao}</div></div>', unsafe_allow_html=True)

            # Gráfico
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(df.index, df['Close'], label='Preço', color='#3498db', linewidth=2)
            ax.plot(df.index, df['SMA20'], label='Média 20 Dias', color='#e74c3c', linestyle='--')
            ax.plot(df.index, df['SMA50'], label='Média 50 Dias', color='#2ecc71', linestyle='--')

            ax.set_facecolor('#1a1a1a')
            fig.patch.set_facecolor('#1a1a1a')
            ax.tick_params(colors='#ecf0f1')
            ax.spines['bottom'].set_color('#4a4a4a')
            ax.spines['top'].set_color('#4a4a4a')
            ax.spines['left'].set_color('#4a4a4a')
            ax.spines['right'].set_color('#4a4a4a')
            ax.grid(color='#4a4a4a', linestyle='--', alpha=0.5)
            ax.legend(facecolor='#2c2c2c', fontsize=10, labelcolor='#ecf0f1')

            st.pyplot(fig)

    except Exception as e:
        st.error(f"Erro ao obter dados: {e}")

else:
    st.info("Digite um ticker válido e clique fora para analisar.")
