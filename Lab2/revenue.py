import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


file_path = 'Lab2/BTCUSDT-1m-2026-02.csv'

columns = [
    "Open time", "Open", "High", "Low", "Close", "Volume",
    "Close time", "Quote asset volume", "Number of trades",
    "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"
]

df = pd.read_csv(file_path, names=columns)

df_btc = df[['Close']].copy()

df_btc['Log_Return'] = np.log(df_btc['Close']) - np.log(df_btc['Close'].shift(1))

df_btc = df_btc.dropna()

returns = df_btc['Log_Return'].values

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.hist(returns, bins=200, density=True, color='steelblue', log=True)
ax1.set_title('Rozkład prawdopodobieństwa stóp zwrotu')
ax1.set_xlabel('Logarytmiczna stopa zwrotu')
ax1.set_ylabel('Gęstość (skala log)')
ax1.grid(True, alpha=0.3)

sorted_returns = np.sort(returns)
p_greater_than_x = 1. - np.arange(1, len(sorted_returns) + 1) / len(sorted_returns)

ax2.plot(sorted_returns, p_greater_than_x, color='darkred')
ax2.set_yscale('log')
ax2.set_xlim(left=0)  
ax2.set_title('Skumulowany rozkład prawdopodobieństwa 1 - F_X(x)')
ax2.set_xlabel('Logarytmiczna stopa zwrotu (x)')
ax2.set_ylabel('P(X > x) (skala log)')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()


returns = df_btc['Log_Return'].values
abs_returns = np.abs(returns)

# Definicja funkcji do obliczania autokorelacji
def calculate_acf(series, max_lag):
    acf_values = []
    mean = np.mean(series)
    var = np.var(series)
    for lag in range(max_lag + 1):
        if lag == 0:
            acf_values.append(1.0)
        else:
            # Wzór na kowariancję z opóźnieniem k
            cov = np.mean((series[:-lag] - mean) * (series[lag:] - mean))
            acf_values.append(cov / var)
    return acf_values

# Delay
max_lag = 100 
acf_returns = calculate_acf(returns, max_lag)
acf_abs_returns = calculate_acf(abs_returns, max_lag)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Wykres 1: ACF dla stóp zwrotu (liniowa skala)
ax1.plot(range(max_lag + 1), acf_returns, color='blue', linewidth=1.5)
ax1.axhline(0, color='black', linewidth=1)
ax1.set_title('Funkcja autokorelacji dla stóp zwrotu')
ax1.set_xlabel(r'Opóźnienie $k$ (w minutach)')
ax1.set_ylabel(r'Autokorelacja $R(k)$')
ax1.grid(True, alpha=0.3)

# Wykres 2: ACF dla modułów stóp zwrotu
ax2.plot(range(max_lag + 1), acf_abs_returns, color='red', linewidth=1.5)
ax2.axhline(0, color='black', linewidth=1)
ax2.set_xscale('log') # Logarytmiczna skala X
ax2.set_yscale('log') # Logarytmiczna skala Y
ax2.set_title('Funkcja autokorelacji dla modułów stóp zwrotu')
ax2.set_xlabel(r'Opóźnienie $k$ (skala log)')
ax2.set_ylabel('Autokorelacja (skala log)')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()