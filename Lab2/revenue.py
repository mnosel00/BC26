import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_acf(series, max_lag):
    """Funkcja obliczająca autokorelację do zadanego opóźnienia."""
    acf_values = []
    mean = np.mean(series)
    var = np.var(series)
    for lag in range(max_lag + 1):
        if lag == 0:
            acf_values.append(1.0)
        else:
            cov = np.mean((series[:-lag] - mean) * (series[lag:] - mean))
            acf_values.append(cov / var)
    return acf_values

columns = [
    "Open time", "Open", "High", "Low", "Close", "Volume",
    "Close time", "Quote asset volume", "Number of trades",
    "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"
]

# Pary
pairs = ['BTCUSDT', 'ETHBTC', 'ETHUSDT']


for pair in pairs:
    print(f"Przetwarzanie lokalnych danych dla: {pair}...")
    
    file_path = f"Lab2/{pair}-1m-2026-02.csv" 
    
    try:
        df = pd.read_csv(file_path, names=columns)
    except FileNotFoundError:
        continue
        
    df_pair = df[['Close']].copy()
    
    # Obliczanie stóp zwrotu
    df_pair['Log_Return'] = np.log(df_pair['Close']) - np.log(df_pair['Close'].shift(1))
    df_pair = df_pair.dropna()
    
    returns = df_pair['Log_Return'].values
    abs_returns = np.abs(returns)
    
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Analiza pary kryptowalutowej {pair}', fontsize=16, fontweight='bold')
    
    # 1. Rozkład stóp zwrotu (Histogram)
    axs[0, 0].hist(returns, bins=200, density=True, color='steelblue', log=True)
    axs[0, 0].set_title('Rozkład prawdopodobieństwa stóp zwrotu')
    axs[0, 0].set_xlabel('Logarytmiczna stopa zwrotu')
    axs[0, 0].set_ylabel('Gęstość (skala log)')
    axs[0, 0].grid(True, alpha=0.3)
    
    # 2. Skumulowany rozkład prawdopodobieństwa
    sorted_returns = np.sort(returns)
    p_greater_than_x = 1. - np.arange(1, len(sorted_returns) + 1) / len(sorted_returns)
    axs[0, 1].plot(sorted_returns, p_greater_than_x, color='darkred')
    axs[0, 1].set_yscale('log')
    axs[0, 1].set_xlim(left=0)
    axs[0, 1].set_title('Skumulowany rozkład 1 - F_X(x)')
    axs[0, 1].set_xlabel('Logarytmiczna stopa zwrotu (x)')
    axs[0, 1].set_ylabel('P(X > x) (skala log)')
    axs[0, 1].grid(True, alpha=0.3)
    
    # 3. Funkcja autokorelacji stóp zwrotu
    max_lag = 100
    acf_returns = calculate_acf(returns, max_lag)
    axs[1, 0].plot(range(max_lag + 1), acf_returns, color='blue', linewidth=1.5)
    axs[1, 0].axhline(0, color='black', linewidth=1)
    axs[1, 0].set_title('Autokorelacja stóp zwrotu')
    axs[1, 0].set_xlabel('Opóźnienie k (w minutach)')
    axs[1, 0].set_ylabel('Autokorelacja R(k)')
    axs[1, 0].grid(True, alpha=0.3)
    
    # 4. Funkcja autokorelacji modułów stóp zwrotu
    acf_abs_returns = calculate_acf(abs_returns, max_lag)
    axs[1, 1].plot(range(max_lag + 1), acf_abs_returns, color='red', linewidth=1.5)
    axs[1, 1].axhline(0, color='black', linewidth=1)
    axs[1, 1].set_xscale('log')
    axs[1, 1].set_yscale('log')
    axs[1, 1].set_title('Autokorelacja modułów stóp zwrotu')
    axs[1, 1].set_xlabel('Opóźnienie k (skala log)')
    axs[1, 1].set_ylabel('Autokorelacja (skala log)')
    axs[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()