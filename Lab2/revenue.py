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
