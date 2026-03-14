import pandas as pd
import matplotlib.pyplot as plt

# Zmuszamy pandas do pokazania wszystkich kolumn w jednej linii
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# Ścieżki do Twoich plików w folderze Lab1
plik_btc_usdt = 'Lab1/BTCUSDT-1s-2026-02.csv'
plik_eth_btc = 'Lab1/ETHBTC-1s-2026-02.csv'
plik_eth_usdt = 'Lab1/ETHUSDT-1s-2026-02.csv'

# Kolumny, które znajdują się w plikach z Binance
kolumny = [
    'open_time', 'open', 'high', 'low', 'close', 'volume', 
    'close_time', 'quote_asset_volume', 'number_of_trades', 
    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
]

def wczytaj_dane(sciezka, nazwa_pary):
    print(f"Wczytuję {nazwa_pary}...")
    df = pd.read_csv(sciezka, names=kolumny)
    # Wyciągamy tylko czas i cenę zamknięcia
    df = df[['close_time', 'close']]
    # Zmieniamy nazwę kolumny 'close' na konkretną, np. 'cena_BTCUSDT'
    df = df.rename(columns={'close': f'cena_{nazwa_pary}'})
    return df

# 1. Wczytywanie plików
df_btc_usdt = wczytaj_dane(plik_btc_usdt, 'BTCUSDT')
df_eth_btc = wczytaj_dane(plik_eth_btc, 'ETHBTC')
df_eth_usdt = wczytaj_dane(plik_eth_usdt, 'ETHUSDT')

# 2. Łączenie w jedną tabelę po czasie (close_time)
print("Łączę tabele...")
df_merged = pd.merge(df_btc_usdt, df_eth_btc, on='close_time')
df_merged = pd.merge(df_merged, df_eth_usdt, on='close_time')

# 3. Matematyka z prezentacji (Szukanie arbitrażu)
print("Obliczam arbitraż...")
# Tworzymy kurs USDT/ETH odwracając ETH/USDT
df_merged['cena_USDTETH'] = 1 / df_merged['cena_ETHUSDT']

# Liczymy iloczyn z prezentacji
df_merged['iloczyn_arbitrazu'] = df_merged['cena_BTCUSDT'] * df_merged['cena_ETHBTC'] * df_merged['cena_USDTETH']

# Wyświetlamy pierwsze kilka wierszy, żeby zobaczyć efekt
print("\nOto pierwsze 5 wierszy gotowej tabeli:")
print(df_merged.head())



print("Rysuję wykres...")

# 1. Konwertujemy te dziwne liczby czasu na czytelną datę
# Używamy formatu milisekund lub mikrosekund (Binance często daje ms z dodatkami)
df_merged['data'] = pd.to_datetime(df_merged['close_time'], unit='us')

# 2. Tworzymy wykres
plt.figure(figsize=(14, 7))

# Rysujemy niebieską linię dla wszystkich naszych wyników
plt.plot(df_merged['data'], df_merged['iloczyn_arbitrazu'], label='Iloczyn arbitrażu', color='blue', alpha=0.6)

# Dodajemy poziomą, zieloną linię na wartości 1.0 (punkt wyjścia na zero)
plt.axhline(y=1, color='green', linestyle='--', label='Granica zysku (1.0)')

# 3. Upiększamy wykres
plt.title('Arbitraż trójkątny USDT -> BTC -> ETH -> USDT')
plt.xlabel('Czas')
plt.ylabel('Wartość początkowego 1 USDT po cyklu')
plt.legend()
plt.grid(True)

# Pokazujemy okienko z wykresem
plt.show()