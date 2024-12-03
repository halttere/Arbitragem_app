import ccxt
import pandas as pd
import streamlit as st

# Função para configurar conexões com as exchanges
def setup_exchanges():
    mexc = ccxt.mexc()  # Conexão com a MEXC
    mercado_bitcoin = ccxt.mercado()  # Conexão com Mercado Bitcoin
    return mexc, mercado_bitcoin

# Função para buscar o livro de ordens
def get_order_book(exchange, symbol):
    try:
        order_book = exchange.fetch_order_book(symbol)
        return order_book
    except Exception as e:
        st.error(f"Erro ao buscar livro de ordens: {e}")
        return None

# Função para buscar preços (bid e ask)
def get_price(exchange, symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker['bid'], ticker['ask']  # Preço de venda (bid) e compra (ask)
    except Exception as e:
        st.error(f"Erro ao buscar preços: {e}")
        return None, None

# Função para calcular arbitragem
def calculate_arbitrage(buy_price, sell_price, fees, transfer_cost):
    if buy_price is None or sell_price is None:
        return None, None
    spread = (sell_price - buy_price) / buy_price * 100
    net_profit = (sell_price - buy_price) - (fees + transfer_cost)
    return spread, net_profit

# Função para verificar liquidez
def check_liquidity(order_book, volume):
    if not order_book:
        return False
    cumulative_volume = 0
    for order in order_book:
        price, size = order[0], order[1]
        cumulative_volume += size * price
        if cumulative_volume >= volume:
            return True
    return False

# Configurações principais
SYMBOL = "BTC/USDT"  # Exemplo: Bitcoin em dólares
TRADE_VOLUME = 1000  # Volume de negociação em dólares
FEES = 0.002  # Taxa de 0.2% por transação
TRANSFER_COST = 0.0005  # Custo de transferência fixo (exemplo)

# Streamlit - Interface do usuário
st.title("Monitoramento de Arbitragem de Criptomoedas")

# Configuração das exchanges
mexc, mercado_bitcoin = setup_exchanges()

# Obter preços de ambas as exchanges
mexc_bid, mexc_ask = get_price(mexc, SYMBOL)
mb_bid, mb_ask = get_price(mercado_bitcoin, SYMBOL)

# Mostrar preços, se disponíveis
st.subheader("Preços")
if mexc_ask is not None and mexc_bid is not None:
    st.write(f"MEXC - Compra (ask): {mexc_ask}, Venda (bid): {mexc_bid}")
else:
    st.error("Erro ao buscar preços da MEXC.")

if mb_ask is not None and mb_bid is not None:
    st.write(f"Mercado Bitcoin - Compra (ask): {mb_ask}, Venda (bid): {mb_bid}")
else:
    st.error("Erro ao buscar preços do Mercado Bitcoin.")

# Verificar se é possível calcular arbitragem
if mexc_ask is not None and mb_bid is not None:
    spread, net_profit = calculate_arbitrage(mexc_ask, mb_bid, FEES, TRANSFER_COST)
    if spread is not None and net_profit is not None:
        st.subheader("Oportunidade de Arbitragem")
        st.write(f"Spread: {spread:.2f}%")
        st.write(f"Lucro líquido estimado: {net_profit:.2f}")
    else:
        st.warning("Não foi possível calcular arbitragem devido a dados incompletos.")
else:
    st.warning("Não foi possível calcular arbitragem devido a preços inválidos.")

# Verificar liquidez
st.subheader("Liquidez")
mexc_book = get_order_book(mexc, SYMBOL)
mb_book = get_order_book(mercado_bitcoin, SYMBOL)

if mexc_book and mb_book:
    mexc_liquidity = check_liquidity(mexc_book['asks'], TRADE_VOLUME)
    mb_liquidity = check_liquidity(mb_book['bids'], TRADE_VOLUME)

    st.write(f"MEXC: {'Suficiente' if mexc_liquidity else 'Insuficiente'}")
    st.write(f"Mercado Bitcoin: {'Suficiente' if mb_liquidity else 'Insuficiente'}")
else:
    st.error("Erro ao buscar liquidez nos livros de ordens.")


