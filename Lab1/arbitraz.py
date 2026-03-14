import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

plik_btc_usdt = 'Lab1/BTCUSDT-1s-2026-02.csv'
plik_eth_btc = 'Lab1/ETHBTC-1s-2026-02.csv'
plik_eth_usdt = 'Lab1/ETHUSDT-1s-2026-02.csv'

kolumny = [
    'open_time', 'open', 'high', 'low', 'close', 'volume', 
    'close_time', 'quote_asset_volume', 'number_of_trades', 
    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
]

def wczytaj_dane(sciezka, nazwa_pary):
    print(f"Wczytuję {nazwa_pary}...")
    df = pd.read_csv(sciezka, names=kolumny)
    df = df[['close_time', 'close']]
    df = df.rename(columns={'close': f'cena_{nazwa_pary}'})
    return df

df_btc_usdt = wczytaj_dane(plik_btc_usdt, 'BTCUSDT')
df_eth_btc = wczytaj_dane(plik_eth_btc, 'ETHBTC')
df_eth_usdt = wczytaj_dane(plik_eth_usdt, 'ETHUSDT')

df_merged = pd.merge(df_btc_usdt, df_eth_btc, on='close_time')
df_merged = pd.merge(df_merged, df_eth_usdt, on='close_time')

df_merged['cena_USDTETH'] = 1 / df_merged['cena_ETHUSDT']

df_merged['iloczyn_arbitrazu'] = df_merged['cena_BTCUSDT'] * df_merged['cena_ETHBTC'] * df_merged['cena_USDTETH']

print(df_merged.head())


df_merged['data'] = pd.to_datetime(df_merged['close_time'], unit='us')

plt.figure(figsize=(14, 7))

plt.plot(df_merged['data'], df_merged['iloczyn_arbitrazu'], label='Iloczyn arbitrażu', color='blue', alpha=0.6)

plt.axhline(y=1, color='green', linestyle='--', label='Granica zysku (1.0)')

plt.title('Arbitraż  USDT -> BTC -> ETH -> USDT')
plt.xlabel('Czas')
plt.ylabel('Wartość początkowego 1 USDT po cyklu')
plt.legend()
plt.grid(True)

plt.show()