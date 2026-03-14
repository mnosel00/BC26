import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

df_bitstamp = pd.read_csv('Lab1/BTC_Bitstamp.csv', header=0, names=['czas', 'cena_Bitstamp'])
df_kraken = pd.read_csv('Lab1/BTC_Kraken.csv', header=0, names=['czas', 'cena_Kraken'])

df_merged = pd.merge(df_bitstamp, df_kraken, on='czas')

df_merged['roznica_cen_USD'] = df_merged['cena_Bitstamp'] - df_merged['cena_Kraken']

df_merged['zysk_brutto_USD'] = abs(df_merged['roznica_cen_USD'])

df_merged['data'] = pd.to_datetime(df_merged['czas'], unit='s')

print(df_merged.head())

plt.figure(figsize=(14, 7))

plt.plot(df_merged['data'], df_merged['zysk_brutto_USD'], label='Zysk brutto z arbitrażu (USD na 1 BTC)', color='purple', alpha=0.7)

plt.axhline(y=0, color='green', linestyle='--', label='Brak różnicy w cenie')

plt.title('Arbitraż BTC między Bitstamp a Kraken')
plt.xlabel('Czas')
plt.ylabel('Różnica w cenie (USD)')
plt.legend()
plt.grid(True)

plt.show()