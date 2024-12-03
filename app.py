pip install ccxt streamlit pandas

import ccxt
import pandas as pd

def get_order_book(exchange, symbol):
    try:
        order_book = exchange.fetch_order_book(symbol)
        return order_book
    except Exception as e:
        print(f"Erro ao buscar book de ordens: {e}")
        return None

def get_price(exchange, symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker['bid'], ticker['ask']  # Preço de venda e compra
    except Exception as e:
        print(f"Erro ao buscar preço: {e}")
        return None, None

def calculate_arbitrage(buy_price, sell_price, fees, transfer_cost):
    spread = (sell_price - buy_price) / buy_price * 100
    net_profit = (sell_price - buy_price) - (fees + transfer_cost)
    return spread, net_profit

def check_liquidity(order_book, volume):
    cumulative_volume = 0
    for order in order_book:
        price, size = order[0], order[1]
        cumulative_volume += size * price
        if cumulative_volume >= volume:
            return True
    return False

def setup_exchanges():
    mexc = ccxt.mexc()  # Conexão com a MEXC
    mercado_bitcoin = ccxt.mercado()  # Conexão com Mercado Bitcoin
    return mexc, mercado_bitcoin

SYMBOL = "BTC/USDT"  # Exemplo: Bitcoin em dólares
TRADE_VOLUME = 1000  # Volume de negociação em dólares
FEES = 0.002  # Taxa de 0.2% por transação
TRANSFER_COST = 0.0005  # Custo de transferência fixo (exemplo)

import streamlit as st

st.title("Monitoramento de Arbitragem de Criptomoedas")

mexc, mercado_bitcoin = setup_exchanges()

# Preços
mexc_bid, mexc_ask = get_price(mexc, SYMBOL)
mb_bid, mb_ask = get_price(mercado_bitcoin, SYMBOL)

# Mostrar preços
st.subheader("Preços")
st.write(f"MEXC - Compra: {mexc_ask}, Venda: {mexc_bid}")
st.write(f"Mercado Bitcoin - Compra: {mb_ask}, Venda: {mb_bid}")

# Arbitragem
spread, net_profit = calculate_arbitrage(mexc_ask, mb_bid, FEES, TRANSFER_COST)

st.subheader("Oportunidade de Arbitragem")
st.write(f"Spread: {spread:.2f}%")
st.write(f"Lucro líquido estimado: {net_profit:.2f}")

# Liquidez
mexc_book = get_order_book(mexc, SYMBOL)
mb_book = get_order_book(mercado_bitcoin, SYMBOL)

if mexc_book and mb_book:
    mexc_liquidity = check_liquidity(mexc_book['asks'], TRADE_VOLUME)
    mb_liquidity = check_liquidity(mb_book['bids'], TRADE_VOLUME)

    st.subheader("Liquidez")
    st.write(f"MEXC: {'Suficiente' if mexc_liquidity else 'Insuficiente'}")
    st.write(f"Mercado Bitcoin: {'Suficiente' if mb_liquidity else 'Insuficiente'}")

