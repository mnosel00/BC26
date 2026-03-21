import math
import time
import requests

# Konfiguracja biblioteki bitcoin-utils:
# ustawiamy sieć testową Bitcoin Testnet
from bitcoinutils.setup import setup

# PrivateKey - obsługa klucza prywatnego
# P2pkhAddress - tworzenie/obsługa adresów legacy P2PKH
from bitcoinutils.keys import PrivateKey, P2pkhAddress

# Klasy do budowania transakcji:
# Transaction - cała transakcja
# TxInput - wejście transakcji
# TxOutput - wyjście transakcji
from bitcoinutils.transactions import Transaction, TxInput, TxOutput

# Script - skrypt Bitcoin Script, używany tu do scriptSig
from bitcoinutils.script import Script

# Ustawiamy sieć testową
setup("testnet")

# Lista publicznych API zgodnych z Esplora.
# Jeśli jedno nie odpowiada, próbujemy następnego.
API_BASES = [
    "https://blockstream.info/testnet/api",
    "https://mempool.space/testnet/api",
]

# Jedna współdzielona sesja HTTP dla requests
SESSION = requests.Session()


def http_get_json(path: str, timeout=(10, 60), retries=3):
    """
    Wysyła GET do kolejnych endpointów API i zwraca JSON.
    Ma retry oraz fallback między różnymi serwerami.
    """
    last_err = None
    for base in API_BASES:
        url = f"{base}{path}"
        for attempt in range(retries):
            try:
                r = SESSION.get(url, timeout=timeout)
                r.raise_for_status()
                return r.json()
            except requests.RequestException as e:
                last_err = e
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"GET failed for {path}: {last_err}")


def http_post_text(path: str, body: str, timeout=(10, 60), retries=3):
    """
    Wysyła POST z tekstowym body, np. raw transaction hex.
    Zwraca odpowiedź jako tekst.
    """
    last_err = None
    headers = {"Content-Type": "text/plain"}
    for base in API_BASES:
        url = f"{base}{path}"
        for attempt in range(retries):
            try:
                r = SESSION.post(url, data=body, headers=headers, timeout=timeout)
                r.raise_for_status()
                return r.text.strip()
            except requests.RequestException as e:
                last_err = e
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"POST failed for {path}: {last_err}")


def get_utxos(address: str):
    """
    Pobiera listę UTXO dla podanego adresu.
    UTXO to niewydane wyjścia, z których można zbudować nową transakcję.
    """
    return http_get_json(f"/address/{address}/utxo")


def get_fee_rate_sat_vb(target_blocks: int = 6) -> float:
    """
    Pobiera przybliżoną stawkę fee w sat/vB.
    """
    data = http_get_json("/fee-estimates")
    return float(data.get(str(target_blocks), data.get("6", 2.0)))


def broadcast_tx(rawtx_hex: str) -> str:
    """
    Wysyła gotową, podpisaną transakcję do sieci testnet.
    Zwraca txid nadanej transakcji.
    """
    return http_post_text("/tx", rawtx_hex)


def estimate_p2pkh_tx_vbytes(num_inputs: int, num_outputs: int) -> int:
    """
    Przybliżenie rozmiaru transakcji legacy P2PKH:
    10 + 148 * inputs + 34 * outputs
    """
    return 10 + 148 * num_inputs + 34 * num_outputs


def main():
    # 1. Klucz prywatny testnet w formacie WIF
    sender_wif = "cPt8jQem9KdQisAXG4K9cEPPZqbUA1FdZ7rm3QxbWwTmxRQ7bhZX"

    # 2. Adres odbiorcy P2PKH testnet
    recipient_address_str = "n1F4cYWCbzN7xFpCsAWo78NWmmjpoMCP59"

    # 3. Kwota do wysłania w satoshi
    amount_to_send = 9_000

    # Tworzymy obiekt klucza prywatnego z WIF
    sender_priv = PrivateKey.from_wif(sender_wif)

    # Wyprowadzamy klucz publiczny
    sender_pub = sender_priv.get_public_key()

    # Wyliczamy adres nadawcy
    sender_addr = sender_pub.get_address()

    print("Sender:", sender_addr.to_string())

    # Pobieramy listę UTXO nadawcy
    utxos = get_utxos(sender_addr.to_string())
    print("UTXO count:", len(utxos))

    if not utxos:
        raise RuntimeError("Brak UTXO na adresie nadawcy")

    # Dla prostoty wybieramy pierwsze UTXO
    utxo = utxos[0]
    txid = utxo["txid"]
    vout = utxo["vout"]
    input_value = int(utxo["value"])

    print("\nWybrane UTXO do wydania:")
    print(f"  txid:   {txid}")
    print(f"  vout:   {vout}")
    print(f"  value:  {input_value} sat")
    print("  pełne dane UTXO:", utxo)

    # ScriptPubKey wydawanego wyjścia
    prev_script_pubkey = sender_addr.to_script_pub_key()

    print("\nScriptPubKey wydawanego wyjścia:")
    print(prev_script_pubkey)
    print("ScriptPubKey hex:", prev_script_pubkey.to_hex())

    # Pobieramy fee rate
    fee_rate = get_fee_rate_sat_vb(6)
    est_vbytes = estimate_p2pkh_tx_vbytes(1, 2)
    fee = math.ceil(fee_rate * est_vbytes)

    print("\nParametry opłaty:")
    print(f"  fee_rate:    {fee_rate} sat/vB")
    print(f"  est_vbytes:  {est_vbytes}")
    print(f"  fee:         {fee} sat")

    # Liczymy change
    change = input_value - amount_to_send - fee

    if change < 546:
        raise RuntimeError(
            f"Za mały change albo za małe UTXO. "
            f"input={input_value}, send={amount_to_send}, fee={fee}, change={change}"
        )

    print("\nPodział środków:")
    print(f"  do odbiorcy: {amount_to_send} sat")
    print(f"  change:      {change} sat")

    # Budujemy wejście transakcji
    txin = TxInput(txid, vout)

    # Budujemy adres odbiorcy
    recipient_addr = P2pkhAddress(recipient_address_str)

    # Tworzymy wyjścia:
    # 1) odbiorca
    # 2) change wraca do nadawcy
    txout_recipient = TxOutput(amount_to_send, recipient_addr.to_script_pub_key())
    txout_change = TxOutput(change, sender_addr.to_script_pub_key())

    print("\nNowe wyjścia transakcji:")
    print("Odbiorca:")
    print(f"  address: {recipient_address_str}")
    print(f"  value:   {amount_to_send} sat")
    print(f"  script:  {recipient_addr.to_script_pub_key().to_hex()}")

    print("Change:")
    print(f"  address: {sender_addr.to_string()}")
    print(f"  value:   {change} sat")
    print(f"  script:  {sender_addr.to_script_pub_key().to_hex()}")

    # Składamy transakcję legacy P2PKH
    tx = Transaction([txin], [txout_recipient, txout_change], has_segwit=False)

    # Podpisujemy wejście nr 0
    signature = sender_priv.sign_input(tx, 0, prev_script_pubkey)

    # Dla P2PKH scriptSig zawiera podpis i klucz publiczny
    txin.script_sig = Script([signature, sender_pub.to_hex()])

    print("\nScriptSig wejścia:")
    print(txin.script_sig)
    print("ScriptSig hex:", txin.script_sig.to_hex())

    # Serializacja do raw hex
    rawtx = tx.serialize()
    print("\nRaw tx:")
    print(rawtx)

    # Broadcast
    broadcasted_txid = broadcast_tx(rawtx)
    print("\nBroadcasted txid:", broadcasted_txid)


if __name__ == "__main__":
    main()