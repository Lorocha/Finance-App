import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy.stats import norm
import warnings
import json
import os
from datetime import datetime

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="OptionLab · Calculadora de Opções",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS — DARK TERMINAL AESTHETIC
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
.stApp { background-color: #0a0e1a; color: #c9d1e0; }
[data-testid="stSidebar"] { background-color: #0d1221 !important; border-right: 1px solid #1e2d4a; }
.sidebar-section {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #4a7ab5;
    margin-top: 18px;
    margin-bottom: 4px;
    border-bottom: 1px solid #1a2540;
    padding-bottom: 4px;
}
[data-testid="stSelectbox"] > div > div,
[data-testid="stNumberInput"] > div > div > input,
[data-testid="stTextInput"] > div > div > input,
[data-testid="stSlider"] > div {
    background-color: #111828 !important;
    border: 1px solid #1e2d4a !important;
    color: #c9d1e0 !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.85rem !important;
}
label, .stLabel {
    color: #8899bb !important;
    font-size: 0.8rem !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
.stButton > button {
    background: linear-gradient(135deg, #1a4b8c 0%, #1e3a6e 100%);
    color: #7eb3ff;
    border: 1px solid #2d5c9e;
    border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 8px 20px;
    width: 100%;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2055a0 0%, #1a4b8c 100%);
    border-color: #4a7ab5;
    color: #a8d0ff;
}
[data-testid="stMetric"] {
    background-color: #0f1c33;
    border: 1px solid #1e2d4a;
    border-radius: 6px;
    padding: 12px 16px;
}
[data-testid="stMetricValue"] {
    color: #7eb3ff !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
.optionlab-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem;
    font-weight: 600;
    color: #7eb3ff;
    letter-spacing: 0.05em;
}
.optionlab-sub {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: #3d6496;
    letter-spacing: 0.18em;
    text-transform: uppercase;
}
.price-card {
    background: linear-gradient(135deg, #0e2040 0%, #0a1628 100%);
    border: 1px solid #2d5c9e;
    border-radius: 8px;
    padding: 20px 24px;
    text-align: center;
    margin: 8px 0;
}
.price-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: #4a7ab5;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.price-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.4rem;
    font-weight: 600;
    color: #7eb3ff;
    line-height: 1;
}
.price-currency { font-size: 1.1rem; color: #4a7ab5; }
.tag-call, .tag-put, .tag-neutral {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 3px;
    letter-spacing: 0.08em;
}
.tag-call { background-color: rgba(34,197,94,0.12); border: 1px solid rgba(34,197,94,0.3); color: #4ade80; }
.tag-put { background-color: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.3); color: #f87171; }
.tag-neutral { background-color: rgba(59,130,246,0.12); border: 1px solid rgba(59,130,246,0.3); color: #7eb3ff; }
.status-found, .status-error, .status-warn {
    border-radius: 6px;
    padding: 10px 14px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
}
.status-found { background: rgba(34,197,94,0.08); border: 1px solid rgba(34,197,94,0.25); color: #4ade80; }
.status-error { background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.25); color: #f87171; }
.status-warn { background: rgba(251,191,36,0.08); border: 1px solid rgba(251,191,36,0.25); color: #fbbf24; }
hr { border-color: #1e2d4a !important; margin: 12px 0 !important; }
#MainMenu { display: none !important; }
footer { display: none !important; }
.block-container { padding-top: 0.5rem !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PLOTLY THEME
# ─────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(10,14,26,0)",
    plot_bgcolor="rgba(13,18,33,0.6)",
    font=dict(family="IBM Plex Mono", color="#8899bb", size=11),
    xaxis=dict(gridcolor="#1a2540", zerolinecolor="#1a2540", linecolor="#1e2d4a"),
    yaxis=dict(gridcolor="#1a2540", zerolinecolor="#1a2540", linecolor="#1e2d4a"),
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(bgcolor="rgba(13,18,33,0.8)", bordercolor="#1e2d4a", borderwidth=1, font=dict(size=10)),
)

# ─────────────────────────────────────────────
# FINANCIAL MODELS
# ─────────────────────────────────────────────
def buscar_ticker(ticker):
    ticker_original = ticker.upper().strip()
    if ".SA" in ticker_original or "^" in ticker_original or "=" in ticker_original:
        return ticker_original

    possibilidades = [ticker_original, f"{ticker_original}.SA"]

    for tentativa in possibilidades:
        try:
            t = yf.Ticker(tentativa)
            hist = t.history(period="5d")
            if not hist.empty:
                return tentativa
        except Exception:
            continue

    return None


def get_stock_data(ticker):
    ticker_correto = buscar_ticker(ticker)

    if not ticker_correto:
        return None, None, None, None, None

    try:
        stock = yf.Ticker(ticker_correto)
        hist = stock.history(period="1y")

        if hist.empty:
            return None, None, None, None, None

        current_price = float(hist["Close"].iloc[-1])
        log_returns = np.log(hist["Close"] / hist["Close"].shift(1)).dropna()
        hist_vol = float(log_returns.std() * np.sqrt(252))

        try:
            nome = stock.info.get("longName", ticker_correto)
        except Exception:
            nome = ticker_correto

        return ticker_correto, current_price, hist_vol, hist, nome

    except Exception:
        return None, None, None, None, None


def bs_d1d2(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2


def black_scholes_call(S, K, T, r, sigma):
    d1, d2 = bs_d1d2(S, K, T, r, sigma)
    return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)


def black_scholes_put(S, K, T, r, sigma):
    d1, d2 = bs_d1d2(S, K, T, r, sigma)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def vega_bs(S, K, T, r, sigma):
    d1, _ = bs_d1d2(S, K, T, r, sigma)
    return S * norm.pdf(d1) * np.sqrt(T)


def greeks(S, K, T, r, sigma, option_type="call"):
    d1, d2 = bs_d1d2(S, K, T, r, sigma)
    vega = S * norm.pdf(d1) * np.sqrt(T) / 100

    if option_type == "call":
        delta = norm.cdf(d1)
        theta = (-(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
        rho = K * T * np.exp(-r * T) * norm.cdf(d2) / 100
    else:
        delta = norm.cdf(d1) - 1
        theta = (-(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
        rho = -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100

    gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))

    return {"delta": delta, "gamma": gamma, "theta": theta, "vega": vega, "rho": rho}


def binomial_tree(S, K, T, r, sigma, n, option_type="call", exercise="european"):
    dt = T / n
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp(r * dt) - d) / (u - d)
    disc = np.exp(-r * dt)

    stock_prices = np.array([S * (u ** (n - i)) * (d**i) for i in range(n + 1)])

    if option_type == "call":
        option_values = np.maximum(stock_prices - K, 0)
    else:
        option_values = np.maximum(K - stock_prices, 0)

    for step in range(n - 1, -1, -1):
        for i in range(step + 1):
            stock_price = S * (u ** (step - i)) * (d**i)
            hold = disc * (p * option_values[i] + (1 - p) * option_values[i + 1])

            if exercise == "american":
                if option_type == "call":
                    exercise_value = max(stock_price - K, 0)
                else:
                    exercise_value = max(K - stock_price, 0)
                option_values[i] = max(hold, exercise_value)
            else:
                option_values[i] = hold

    return option_values[0]


def monte_carlo(S, K, T, r, sigma, n_sims, n_steps, option_type="call", payoff_type="european", seed=42):
    np.random.seed(seed)
    dt = T / n_steps
    Z = np.random.standard_normal((n_sims, n_steps))
    increments = np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z)
    paths = S * np.cumprod(np.hstack([np.ones((n_sims, 1)), increments]), axis=1)

    if payoff_type == "asian":
        avg = paths.mean(axis=1)
        payoff = np.maximum(avg - K, 0) if option_type == "call" else np.maximum(K - avg, 0)
    else:
        S_T = paths[:, -1]
        payoff = np.maximum(S_T - K, 0) if option_type == "call" else np.maximum(K - S_T, 0)

    price = np.exp(-r * T) * payoff.mean()
    std_err = payoff.std() / np.sqrt(n_sims) * np.exp(-r * T)

    return price, std_err, paths


def implied_vol_newton(market_price, S, K, T, r, option_type="call", tol=1e-8, max_iter=200):
    sigma = 0.3

    for _ in range(max_iter):
        price = black_scholes_call(S, K, T, r, sigma) if option_type == "call" else black_scholes_put(S, K, T, r, sigma)
        v = vega_bs(S, K, T, r, sigma)
        diff = price - market_price

        if abs(diff) < tol:
            return sigma

        if v < 1e-10:
            break

        sigma -= diff / v
        sigma = max(0.001, min(10.0, sigma))

    return None


def implied_vol_bisection(market_price, S, K, T, r, option_type="call", tol=1e-8, max_iter=500):
    lo, hi = 0.001, 10.0

    for _ in range(max_iter):
        mid = (lo + hi) / 2
        price = black_scholes_call(S, K, T, r, mid) if option_type == "call" else black_scholes_put(S, K, T, r, mid)
        diff = price - market_price

        if abs(diff) < tol:
            return mid

        if diff > 0:
            hi = mid
        else:
            lo = mid

    return (lo + hi) / 2

# ─────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────
def plot_price_history(hist, nome, ticker):
    log_ret = np.log(hist["Close"] / hist["Close"].shift(1)).dropna()
    rolling_vol = log_ret.rolling(20).std() * np.sqrt(252) * 100

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.55, 0.25, 0.2],
        vertical_spacing=0.04,
        subplot_titles=("Preço de Fechamento", "Vol. Histórica 20d (%)", "Volume"),
    )

    fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode="lines", line=dict(color="#3b82f6", width=1.5), name="Preço"), row=1, col=1)
    fig.add_trace(go.Scatter(x=rolling_vol.index, y=rolling_vol, mode="lines", line=dict(color="#f59e0b", width=1.2), name="Vol 20d"), row=2, col=1)

    if "Volume" in hist.columns:
        fig.add_trace(go.Bar(x=hist.index, y=hist["Volume"], marker_color="rgba(59,130,246,0.3)", name="Volume"), row=3, col=1)

    fig.update_layout(**PLOT_LAYOUT, height=420, showlegend=False, title=dict(text=f"{nome} · {ticker}", font=dict(color="#7eb3ff", size=13), x=0))

    for ann in fig.layout.annotations:
        ann.font.color = "#4a7ab5"
        ann.font.size = 10

    return fig


def plot_payoff(S0, K, option_type, price_theory=None):
    S_range = np.linspace(max(0.01, S0 * 0.4), S0 * 1.7, 300)

    if option_type == "call":
        payoff = np.maximum(S_range - K, 0)
        profit = payoff - (price_theory or 0)
        color_payoff = "#3b82f6"
        color_profit = "#4ade80"
        label = "CALL"
    else:
        payoff = np.maximum(K - S_range, 0)
        profit = payoff - (price_theory or 0)
        color_payoff = "#8b5cf6"
        color_profit = "#f87171"
        label = "PUT"

    fig = go.Figure()

    if price_theory:
        fig.add_trace(go.Scatter(x=S_range, y=profit, mode="lines", line=dict(color=color_profit, width=1.5, dash="dot"), name="Lucro/Prejuízo"))

    fig.add_trace(go.Scatter(x=S_range, y=payoff, mode="lines", line=dict(color=color_payoff, width=2.5), name=f"Payoff {label}"))
    fig.add_vline(x=K, line_dash="dash", line_color="#fbbf24", line_width=1.5, annotation_text=f"Strike R${K:.2f}")
    fig.add_vline(x=S0, line_dash="dot", line_color="#a78bfa", line_width=1.5, annotation_text=f"Spot R${S0:.2f}")
    fig.add_hline(y=0, line_color="#1e2d4a", line_width=1)
    fig.update_layout(**PLOT_LAYOUT, height=320, title=dict(text=f"Payoff — {label}", font=dict(color="#7eb3ff", size=13), x=0))

    return fig


def plot_mc_paths(paths, K, option_type, n_show=80):
    fig = go.Figure()
    show = min(n_show, paths.shape[0])
    steps = np.arange(paths.shape[1])

    for i in range(show):
        fig.add_trace(go.Scatter(x=steps, y=paths[i], mode="lines", line=dict(color="rgba(59,130,246,0.12)", width=0.8), showlegend=False, hoverinfo="skip"))

    mean_path = paths.mean(axis=0)
    fig.add_trace(go.Scatter(x=steps, y=mean_path, mode="lines", line=dict(color="#7eb3ff", width=2.5), name="Trajetória Média"))
    fig.add_hline(y=K, line_dash="dash", line_color="#fbbf24", line_width=1.5, annotation_text=f"Strike K={K:.2f}")
    fig.update_layout(**PLOT_LAYOUT, height=320, title=dict(text=f"Simulação Monte Carlo ({paths.shape[0]:,} trajetórias)", font=dict(color="#7eb3ff", size=13), x=0))

    return fig


def plot_mc_distribution(paths, K, option_type):
    S_T = paths[:, -1]
    payoff = np.maximum(S_T - K, 0) if option_type == "call" else np.maximum(K - S_T, 0)

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Distribuição de S(T)", "Distribuição de Payoffs"))
    fig.add_trace(go.Histogram(x=S_T, nbinsx=60, marker_color="rgba(59,130,246,0.5)", name="S(T)"), row=1, col=1)
    fig.add_trace(go.Histogram(x=payoff, nbinsx=60, marker_color="rgba(74,222,128,0.5)", name="Payoff"), row=1, col=2)
    fig.add_vline(x=K, line_dash="dash", line_color="#fbbf24", row=1, col=1)
    fig.update_layout(**PLOT_LAYOUT, height=280, showlegend=False, title=dict(text="Distribuições — Monte Carlo", font=dict(color="#7eb3ff", size=13), x=0))

    for ann in fig.layout.annotations:
        ann.font.color = "#4a7ab5"
        ann.font.size = 10

    return fig


def plot_greeks_sensitivity(S0, K, T, r, sigma, option_type):
    S_range = np.linspace(S0 * 0.5, S0 * 1.5, 200)
    deltas, gammas, thetas, vegas = [], [], [], []

    for s in S_range:
        g = greeks(s, K, T, r, sigma, option_type)
        deltas.append(g["delta"])
        gammas.append(g["gamma"])
        thetas.append(g["theta"])
        vegas.append(g["vega"])

    fig = make_subplots(rows=2, cols=2, subplot_titles=("Delta", "Gamma", "Theta (por dia)", "Vega (por 1%)"), vertical_spacing=0.14, horizontal_spacing=0.1)

    for (i, j), (vals, color, name) in zip(
        [(1, 1), (1, 2), (2, 1), (2, 2)],
        [(deltas, "#3b82f6", "Delta"), (gammas, "#8b5cf6", "Gamma"), (thetas, "#f59e0b", "Theta"), (vegas, "#4ade80", "Vega")],
    ):
        fig.add_trace(go.Scatter(x=S_range, y=vals, mode="lines", line=dict(color=color, width=1.8), name=name, showlegend=False), row=i, col=j)
        fig.add_vline(x=S0, line_dash="dot", line_color="rgba(255,255,255,0.2)", row=i, col=j)
        fig.add_vline(x=K, line_dash="dash", line_color="rgba(251,191,36,0.4)", row=i, col=j)

    fig.update_layout(**PLOT_LAYOUT, height=380, title=dict(text="Greeks — Sensibilidade ao Preço do Ativo", font=dict(color="#7eb3ff", size=13), x=0))

    for ann in fig.layout.annotations:
        ann.font.color = "#4a7ab5"
        ann.font.size = 10

    return fig


def plot_comparison(results):
    methods = list(results.keys())
    prices = [results[m]["price"] for m in methods]
    colors = ["#3b82f6", "#8b5cf6", "#4ade80"][: len(methods)]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=methods, y=prices, marker_color=colors, text=[f"R$ {p:.4f}" for p in prices], textposition="outside"))
    fig.update_layout(**PLOT_LAYOUT, height=280, title=dict(text="Comparação entre Métodos", font=dict(color="#7eb3ff", size=13), x=0), yaxis_title="Preço Teórico (R$)", showlegend=False)

    return fig

# ─────────────────────────────────────────────
# HISTORY KEEPER
# ─────────────────────────────────────────────
HISTORY_FILE = "history/stock_history.json"


def load_stock_history():
    if not os.path.exists(HISTORY_FILE):
        return {}

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}


def save_stock_to_history(ticker, nome, price, vol):
    os.makedirs("history", exist_ok=True)
    history = load_stock_history()

    if ticker not in history:
        history[ticker] = {
            "ticker": ticker,
            "nome": nome,
            "last_price": round(float(price), 2),
            "hist_vol": round(float(vol) * 100, 2),
            "last_search": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "calculations": [],
        }
    else:
        history[ticker]["nome"] = nome
        history[ticker]["last_price"] = round(float(price), 2)
        history[ticker]["hist_vol"] = round(float(vol) * 100, 2)
        history[ticker]["last_search"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history[ticker].setdefault("calculations", [])

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)


def save_calculation_to_history(ticker, calculation_data):
    os.makedirs("history", exist_ok=True)
    history = load_stock_history()

    if ticker not in history:
        history[ticker] = {
            "ticker": ticker,
            "nome": ticker,
            "last_price": None,
            "hist_vol": None,
            "last_search": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "calculations": [],
        }

    history[ticker].setdefault("calculations", [])
    history[ticker]["calculations"].append(calculation_data)

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)


def delete_stock_from_history(ticker):
    history = load_stock_history()

    if ticker in history:
        del history[ticker]

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=4, ensure_ascii=False)

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
for key, default in [
    ("stock_data", None),
    ("ticker_name", ""),
    ("ticker_symbol", ""),
    ("current_price", 0.0),
    ("hist_vol", 0.30),
    ("hist_df", None),
    ("last_result", None),
    ("mc_paths", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="optionlab-header">OptionLab</div>
<div class="optionlab-sub">Calculadora de Derivativos · FGV EAESP</div>
""", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace; font-size:0.9rem; font-weight:600; color:#7eb3ff; letter-spacing:0.08em;">
    ⬡ CONFIGURAÇÃO
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">01 · Ativo</div>', unsafe_allow_html=True)

    col_t, col_btn = st.columns([3, 2])

    with col_t:
        ticker_input = st.text_input("Ticker", value="PETR4", placeholder="PETR4, AAPL, ^BVSP", label_visibility="collapsed")

    with col_btn:
        fetch_btn = st.button("↓ Buscar", key="fetch")

    if fetch_btn and ticker_input:
        with st.spinner("Buscando..."):
            result = get_stock_data(ticker_input)

        if result[0]:
            ticker_correto, price, vol, hist, nome = result

            st.session_state.stock_data = result
            st.session_state.ticker_symbol = ticker_correto
            st.session_state.ticker_name = nome
            st.session_state.current_price = price
            st.session_state.hist_vol = vol
            st.session_state.hist_df = hist

            save_stock_to_history(ticker_correto, nome, price, vol)

            st.markdown(f"""
            <div class="status-found">
            ✓ {nome}<br>
            Spot: <b>R$ {price:.2f}</b> &nbsp;|&nbsp; Vol: <b>{vol*100:.1f}%</b>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="status-error">✕ Ticker "{ticker_input}" não encontrado</div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">02 · Parâmetros</div>', unsafe_allow_html=True)

    S0 = st.number_input("Preço atual (S₀)", value=float(st.session_state.current_price) or 38.0, min_value=0.01, step=0.5, format="%.2f")
    K = st.number_input("Strike (K)", value=40.0, min_value=0.01, step=0.5, format="%.2f")
    T_days = st.number_input("Vencimento (dias)", value=180, min_value=1, max_value=3650, step=1)
    T = T_days / 365.0
    r_pct = st.number_input("Taxa livre de risco (%)", value=10.5, min_value=0.0, max_value=50.0, step=0.25, format="%.2f")
    r = r_pct / 100.0

    sigma_default = max(float(st.session_state.hist_vol or 0.30), 0.01)
    sigma_pct = st.number_input("Volatilidade anual (%)", value=round(sigma_default * 100, 2), min_value=0.1, max_value=500.0, step=0.5, format="%.2f")
    sigma = sigma_pct / 100.0

    st.markdown('<div class="sidebar-section">03 · Tipo de Opção</div>', unsafe_allow_html=True)

    option_type = st.radio("Payoff", ["Call", "Put"], horizontal=True)
    option_style = st.radio("Estilo", ["Europeia", "Americana", "Asiática"], horizontal=False)

    st.markdown('<div class="sidebar-section">04 · Método</div>', unsafe_allow_html=True)

    method = st.selectbox("Método de precificação", ["Black-Scholes", "Monte Carlo", "Árvore Binomial", "Todos (comparação)"], label_visibility="collapsed")

    show_advanced = st.toggle("Parâmetros avançados", value=False)

    if show_advanced:
        n_sims = st.number_input("Simulações (MC)", value=10000, min_value=1000, max_value=200000, step=1000)
        n_steps_mc = st.number_input("Passos (MC)", value=100, min_value=10, max_value=500, step=10)
        n_nodes = st.number_input("Nós (Binomial)", value=200, min_value=10, max_value=1000, step=10)
    else:
        n_sims = 10000
        n_steps_mc = 100
        n_nodes = 200

    st.markdown('<div class="sidebar-section">05 · Vol. Implícita</div>', unsafe_allow_html=True)

    market_price = st.number_input("Preço de mercado da opção", value=0.0, min_value=0.0, step=0.01, format="%.4f")
    iv_method = st.radio("Método VI", ["Newton-Raphson", "Bisseção"], horizontal=True)

    st.markdown("<br>", unsafe_allow_html=True)
    calc_btn = st.button("▶ CALCULAR", key="calc")
    compare_btn = st.button("⬡ COMPARAR MÉTODOS", key="compare")

# ─────────────────────────────────────────────
# MAIN AREA — TABS
# ─────────────────────────────────────────────
if S0 > 0 and K > 0:
    m = S0 / K
    if option_type == "Call":
        if m > 1.02:
            moneyness = "🟢 ITM"
        elif m < 0.98:
            moneyness = "🔴 OTM"
        else:
            moneyness = "🟡 ATM"
    else:
        if m < 0.98:
            moneyness = "🟢 ITM"
        elif m > 1.02:
            moneyness = "🔴 OTM"
        else:
            moneyness = "🟡 ATM"
else:
    moneyness = "—"

tab_result, tab_market, tab_greeks, tab_mc, tab_compare, tab_history = st.tabs([
    "📊 Resultado",
    "📈 Ativo",
    "Δ Greeks",
    "🎲 Monte Carlo",
    "⚖ Comparação",
    "🕘 Histórico",
])

# ─── TAB: RESULTADO ───
with tab_result:
    if calc_btn or compare_btn:
        ot = option_type.lower()
        es = option_style.lower()

        if method == "Black-Scholes" and es != "europeia":
            st.markdown('<div class="status-warn">⚠ Black-Scholes é estritamente válido apenas para opções europeias. Resultado é aproximado.</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

        results = {}

        methods_to_run = ["Black-Scholes", "Monte Carlo", "Árvore Binomial"] if method == "Todos (comparação)" or compare_btn else [method]

        for m_name in methods_to_run:
            if m_name == "Black-Scholes":
                p = black_scholes_call(S0, K, T, r, sigma) if ot == "call" else black_scholes_put(S0, K, T, r, sigma)
                results[m_name] = {"price": p, "extra": ""}

            elif m_name == "Monte Carlo":
                payoff_type = "asian" if es == "asiática" else "european"
                with st.spinner("Rodando Monte Carlo..."):
                    p, std_err, paths_arr = monte_carlo(S0, K, T, r, sigma, n_sims, n_steps_mc, ot, payoff_type)
                results[m_name] = {"price": p, "extra": f"±{std_err:.4f} (1σ)", "std_err": std_err}
                st.session_state.mc_paths = paths_arr

            elif m_name == "Árvore Binomial":
                exercise = "american" if es == "americana" else "european"
                p = binomial_tree(S0, K, T, r, sigma, n_nodes, ot, exercise)
                results[m_name] = {"price": p, "extra": f"{n_nodes} nós"}

        st.session_state.last_result = results

        active_ticker = st.session_state.ticker_symbol or ticker_input.upper().strip()

        calculation_data = {
            "calculated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ticker": active_ticker,
            "stock_name": st.session_state.ticker_name,
            "option_type": option_type,
            "option_style": option_style,
            "method_selected": method,
            "S0": round(float(S0), 4),
            "K": round(float(K), 4),
            "T_days": int(T_days),
            "r_pct": round(float(r_pct), 4),
            "sigma_pct": round(float(sigma_pct), 4),
            "market_price": round(float(market_price), 4),
            "moneyness": moneyness,
            "results": {
                method_name: {
                    "price": round(float(result_data["price"]), 6),
                    "extra": result_data.get("extra", ""),
                }
                for method_name, result_data in results.items()
            },
        }

        save_calculation_to_history(active_ticker, calculation_data)

        main_price = results[methods_to_run[0]]["price"]

        col_price, col_meta = st.columns([2, 3])

        with col_price:
            tag_class = "tag-call" if ot == "call" else "tag-put"
            tag = option_type.upper()
            st.markdown(f"""
            <div class="price-card">
                <div class="price-label">Preço Teórico · {method}</div>
                <div class="price-value"><span class="price-currency">R$ </span>{main_price:.4f}</div>
                <br>
                <span class="{tag_class}">{tag}</span>
                <span class="tag-neutral" style="margin-left:6px;">{option_style.upper()}</span>
                <span class="tag-neutral" style="margin-left:6px;">{moneyness}</span>
            </div>
            """, unsafe_allow_html=True)

        with col_meta:
            st.markdown("**Parâmetros utilizados**")
            params_data = {
                "Parâmetro": ["S₀ (spot)", "K (strike)", "T (prazo)", "r (taxa)", "σ (vol)"],
                "Valor": [f"R$ {S0:.2f}", f"R$ {K:.2f}", f"{T_days}d ({T:.3f}a)", f"{r_pct:.2f}%", f"{sigma_pct:.2f}%"],
            }
            st.dataframe(pd.DataFrame(params_data), hide_index=True, use_container_width=True, height=210)

        st.markdown("<br>", unsafe_allow_html=True)

        g = greeks(S0, K, T, r, sigma, ot)
        st.markdown("**Greeks (Black-Scholes)**")
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Delta (Δ)", f"{g['delta']:.4f}")
        c2.metric("Gamma (Γ)", f"{g['gamma']:.5f}")
        c3.metric("Theta (Θ)", f"{g['theta']:.4f}")
        c4.metric("Vega (ν)", f"{g['vega']:.4f}")
        c5.metric("Rho (ρ)", f"{g['rho']:.4f}")

        if market_price > 0:
            st.markdown("---")
            st.markdown("**Volatilidade Implícita**")

            if iv_method == "Newton-Raphson":
                iv = implied_vol_newton(market_price, S0, K, T, r, ot)
            else:
                iv = implied_vol_bisection(market_price, S0, K, T, r, ot)

            if iv:
                col_iv1, col_iv2, col_iv3 = st.columns(3)
                col_iv1.metric("Vol. Implícita", f"{iv*100:.4f}%")
                col_iv2.metric("Vol. Histórica", f"{sigma_pct:.2f}%")
                diff_pct = (iv - sigma) / sigma * 100 if sigma > 0 else 0
                col_iv3.metric("Diferença IV−HV", f"{diff_pct:+.1f}%", delta_color="off")
            else:
                st.markdown('<div class="status-error">✕ Não foi possível calcular a vol. implícita.</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Diagrama de Payoff**")
        st.plotly_chart(plot_payoff(S0, K, ot, main_price), use_container_width=True, config={"displayModeBar": False})

    else:
        st.markdown("""
        <div style="text-align:center; padding:60px 20px; color:#2d5c9e; font-family:'IBM Plex Mono',monospace; font-size:0.85rem;">
            ← Configure os parâmetros no painel lateral<br>e pressione <b style="color:#3b82f6">▶ CALCULAR</b>
        </div>
        """, unsafe_allow_html=True)

# ─── TAB: ATIVO ───
with tab_market:
    if st.session_state.hist_df is not None:
        hist = st.session_state.hist_df
        nome = st.session_state.ticker_name
        sym = st.session_state.ticker_symbol
        price = st.session_state.current_price
        vol = st.session_state.hist_vol

        log_ret = np.log(hist["Close"] / hist["Close"].shift(1)).dropna()

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Preço Atual", f"R$ {price:.2f}")
        c2.metric("Vol. Anual (1a)", f"{vol*100:.1f}%")
        c3.metric("Retorno 1a", f"{((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100:.1f}%")
        c4.metric("Máx 52s", f"R$ {hist['High'].max():.2f}")
        c5.metric("Mín 52s", f"R$ {hist['Low'].min():.2f}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.plotly_chart(plot_price_history(hist, nome, sym), use_container_width=True, config={"displayModeBar": False})

        with st.expander("Distribuição dos Retornos Diários"):
            fig_ret = go.Figure()
            fig_ret.add_trace(go.Histogram(x=log_ret * 100, nbinsx=60, marker_color="rgba(59,130,246,0.5)", name="Retorno diário (%)"))
            fig_ret.update_layout(**PLOT_LAYOUT, height=250, xaxis_title="Retorno Diário (%)", title=dict(text="Distribuição de Retornos Logarítmicos", font=dict(color="#7eb3ff", size=13), x=0))
            st.plotly_chart(fig_ret, use_container_width=True, config={"displayModeBar": False})
    else:
        st.markdown("""
        <div style="text-align:center; padding:60px 20px; color:#2d5c9e; font-family:'IBM Plex Mono',monospace; font-size:0.85rem;">
            Digite um ticker e clique <b style="color:#3b82f6">↓ Buscar</b> para carregar dados do ativo.
        </div>
        """, unsafe_allow_html=True)

# ─── TAB: GREEKS ───
with tab_greeks:
    if S0 > 0 and K > 0 and T > 0 and sigma > 0:
        ot = option_type.lower()
        st.plotly_chart(plot_greeks_sensitivity(S0, K, T, r, sigma, ot), use_container_width=True, config={"displayModeBar": False})

        sigma_range = np.linspace(0.05, 1.5, 200)
        prices_sig = [black_scholes_call(S0, K, T, r, s) if ot == "call" else black_scholes_put(S0, K, T, r, s) for s in sigma_range]
        vegas_sig = [vega_bs(S0, K, T, r, s) / 100 for s in sigma_range]

        fig_sig = make_subplots(rows=1, cols=2, subplot_titles=("Preço × Volatilidade", "Vega × Volatilidade"))
        fig_sig.add_trace(go.Scatter(x=sigma_range * 100, y=prices_sig, mode="lines", line=dict(color="#3b82f6", width=2), name="Preço"), row=1, col=1)
        fig_sig.add_trace(go.Scatter(x=sigma_range * 100, y=vegas_sig, mode="lines", line=dict(color="#8b5cf6", width=2), name="Vega"), row=1, col=2)
        fig_sig.add_vline(x=sigma_pct, line_dash="dot", line_color="#fbbf24", row=1, col=1)
        fig_sig.add_vline(x=sigma_pct, line_dash="dot", line_color="#fbbf24", row=1, col=2)
        fig_sig.update_layout(**PLOT_LAYOUT, height=300, showlegend=False, title=dict(text="Sensibilidade à Volatilidade", font=dict(color="#7eb3ff", size=13), x=0))
        st.plotly_chart(fig_sig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Configure os parâmetros para visualizar os Greeks.")

# ─── TAB: MONTE CARLO ───
with tab_mc:
    if st.session_state.mc_paths is not None:
        paths = st.session_state.mc_paths
        ot = option_type.lower()
        st.plotly_chart(plot_mc_paths(paths, K, ot, n_show=100), use_container_width=True, config={"displayModeBar": False})
        st.plotly_chart(plot_mc_distribution(paths, K, ot), use_container_width=True, config={"displayModeBar": False})

        S_T = paths[:, -1]
        payoff = np.maximum(S_T - K, 0) if ot == "call" else np.maximum(K - S_T, 0)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Média S(T)", f"R$ {S_T.mean():.2f}")
        c2.metric("% Exercício", f"{(payoff > 0).mean() * 100:.1f}%")
        c3.metric("Payoff Médio", f"R$ {payoff.mean():.4f}")
        c4.metric("Payoff Máximo", f"R$ {payoff.max():.2f}")
    else:
        st.markdown("""
        <div style="text-align:center; padding:60px 20px; color:#2d5c9e; font-family:'IBM Plex Mono',monospace; font-size:0.85rem;">
            Selecione <b>Monte Carlo</b> como método e pressione <b style="color:#3b82f6">▶ CALCULAR</b>.
        </div>
        """, unsafe_allow_html=True)

# ─── TAB: COMPARAÇÃO ───
with tab_compare:
    if st.session_state.last_result and len(st.session_state.last_result) > 0:
        results = st.session_state.last_result

        if len(results) > 1:
            st.plotly_chart(plot_comparison(results), use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("Use **⬡ COMPARAR MÉTODOS** ou selecione **Todos** para comparar os três métodos simultaneamente.")

        rows = []
        for mname, res in results.items():
            rows.append({"Método": mname, "Preço Teórico": f"R$ {res['price']:.4f}", "Informação Extra": res.get("extra", "—")})

        st.markdown("**Tabela Comparativa**")
        st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

        with st.expander("ℹ Notas sobre os Métodos"):
            st.markdown("""
            | Método | Europeia | Americana | Asiática | Observações |
            |---|---|---|---|---|
            | Black-Scholes | ✅ Exato | ⚠ Aproximado | ❌ | Fórmula fechada, rápido |
            | Monte Carlo | ✅ | ⚠ Limitado | ✅ | Flexível, custo computacional |
            | Árvore Binomial | ✅ | ✅ | ⚠ Possível | Captura exercício antecipado |
            """)
    else:
        st.info("Calcule pelo menos uma precificação para ver a comparação.")

# ─── TAB: HISTÓRICO ───
with tab_history:
    st.markdown("### Histórico de ativos e modelos")

    history = load_stock_history()

    if not history:
        st.info("Nenhum ativo pesquisado ainda. Busque um ticker na barra lateral para começar.")
    else:
        summary_rows = []
        for ticker, data in history.items():
            summary_rows.append({
                "ticker": ticker,
                "nome": data.get("nome", ""),
                "last_price": data.get("last_price", ""),
                "hist_vol": data.get("hist_vol", ""),
                "last_search": data.get("last_search", ""),
                "saved_models": len(data.get("calculations", [])),
            })

        history_df = pd.DataFrame(summary_rows).sort_values("last_search", ascending=False)

        st.markdown("**Ativos pesquisados**")
        st.dataframe(history_df, use_container_width=True, hide_index=True)

        selected_ticker = st.selectbox(
            "Selecionar ativo salvo",
            options=list(history.keys())
        )

        selected_data = history[selected_ticker]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ticker", selected_data.get("ticker", selected_ticker))
        c2.metric("Último preço", f"R$ {selected_data.get('last_price', 0):.2f}" if selected_data.get("last_price") is not None else "—")
        c3.metric("Vol. histórica", f"{selected_data.get('hist_vol', 0):.2f}%" if selected_data.get("hist_vol") is not None else "—")
        c4.metric("Modelos salvos", len(selected_data.get("calculations", [])))

        col_load, col_delete = st.columns(2)

        with col_load:
            if st.button("Carregar ativo"):
                with st.spinner("Carregando ativo..."):
                    result = get_stock_data(selected_ticker)

                if result[0]:
                    ticker_correto, price, vol, hist, nome = result

                    st.session_state.stock_data = result
                    st.session_state.ticker_symbol = ticker_correto
                    st.session_state.ticker_name = nome
                    st.session_state.current_price = price
                    st.session_state.hist_vol = vol
                    st.session_state.hist_df = hist

                    save_stock_to_history(ticker_correto, nome, price, vol)

                    st.success(f"{ticker_correto} carregado com sucesso.")
                    st.rerun()
                else:
                    st.error("Não foi possível carregar esse ativo.")

        with col_delete:
            if st.button("Remover ativo e modelos"):
                delete_stock_from_history(selected_ticker)
                st.success(f"{selected_ticker} removido do histórico.")
                st.rerun()

        st.markdown("---")
        st.markdown("**Modelos salvos para este ativo**")

        calculations = selected_data.get("calculations", [])

        if not calculations:
            st.info("Esse ativo ainda não possui modelos salvos. Calcule uma opção para salvar o primeiro modelo.")
        else:
            calc_rows = []
            for i, calc in enumerate(calculations, start=1):
                result_summary = []
                for method_name, result_data in calc.get("results", {}).items():
                    result_summary.append(f"{method_name}: R$ {result_data.get('price', 0):.4f}")

                calc_rows.append({
                    "#": i,
                    "calculated_at": calc.get("calculated_at", ""),
                    "option_type": calc.get("option_type", ""),
                    "option_style": calc.get("option_style", ""),
                    "method": calc.get("method_selected", ""),
                    "S0": calc.get("S0", ""),
                    "K": calc.get("K", ""),
                    "T_days": calc.get("T_days", ""),
                    "r_pct": calc.get("r_pct", ""),
                    "sigma_pct": calc.get("sigma_pct", ""),
                    "moneyness": calc.get("moneyness", ""),
                    "results": " | ".join(result_summary),
                })

            calc_df = pd.DataFrame(calc_rows).sort_values("calculated_at", ascending=False)
            st.dataframe(calc_df, use_container_width=True, hide_index=True)

            selected_calc_number = st.selectbox(
                "Ver detalhes de um modelo salvo",
                options=[row["#"] for row in calc_rows]
            )

            selected_calc = calculations[selected_calc_number - 1]

            with st.expander("Detalhes completos do modelo selecionado", expanded=True):
                st.json(selected_calc)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<hr>
<div style="font-family:'IBM Plex Mono',monospace; font-size:0.65rem; color:#2d5c9e; text-align:center; padding:8px 0;">
OptionLab · Curso de Gestão de Riscos e Derivativos · FGV EAESP &nbsp;·&nbsp;
Black-Scholes · Monte Carlo · Árvore Binomial · Volatilidade Implícita &nbsp;·&nbsp;
Dados: Yahoo Finance (yfinance)
</div>
""", unsafe_allow_html=True)
