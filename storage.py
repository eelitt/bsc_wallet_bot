import json
import os
import logging

from bsc_utils import is_valid_address, to_checksum_address

WALLET_FILE = 'wallets.json'  # Tiedosto lompakoille
TOKEN_FILE = 'tokens.json'    # Tiedosto tokeneille (dict symbol -> contract)

wallets = {}  # Dict lompakoille (osoite -> {})
tokens = {}   # Dict tokeneille (symbol -> contract)

# Funktio lompakoiden lataamiseen tiedostosta
def load_wallets():
    global wallets
    if os.path.exists(WALLET_FILE):
        try:
            with open(WALLET_FILE, 'r') as f:
                data = json.load(f)
                wallets = {}  # Alusta tyhjäksi
                for addr, val in data.items():
                    if is_valid_address(addr):
                        checksum_addr = to_checksum_address(addr)
                        if checksum_addr not in wallets:  # Estä duplikaatit (jos vanhoja eri caseilla)
                            wallets[checksum_addr] = val
                    else:
                        logging.error(f"Invalidi osoite wallets.json:ssa: {addr} – ohitetaan.")
        except json.JSONDecodeError:
            raise ValueError("Virheellinen JSON tiedostossa")
        except Exception as e:
            raise RuntimeError(f"Virhe tiedoston lukemisessa: {e}")
    else:
        # Luo tyhjä tiedosto jos puuttuu
        save_wallets()

# Funktio tokenien lataamiseen tiedostosta
def load_tokens():
    global tokens
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as f:
                tokens = json.load(f)
        except json.JSONDecodeError:
            raise ValueError("Virheellinen JSON tiedostossa")
        except Exception as e:
            raise RuntimeError(f"Virhe tiedoston lukemisessa: {e}")
    else:
        # Luo tyhjä tiedosto jos puuttuu
        save_tokens()

# Funktio lompakoiden tallentamiseen tiedostoon
def save_wallets():
    try:
        with open(WALLET_FILE, 'w') as f:
            json.dump(wallets, f, indent=4)
    except Exception as e:
        raise RuntimeError(f"Virhe tiedoston kirjoittamisessa: {e}")

# Funktio tokenien tallentamiseen tiedostoon
def save_tokens():
    try:
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f, indent=4)
    except Exception as e:
        raise RuntimeError(f"Virhe tiedoston kirjoittamisessa: {e}")

# Funktio lompakon lisäämiseen (tarkistaa duplikaatit)
def add_wallet(address: str):
    if address in wallets:
        raise ValueError("Lompakko on jo lisätty.")
    
    wallets[address] = {}  # Alusta tyhjillä balansseilla
    save_wallets()

# Funktio kaikkien lompakkojen hakemiseen (palauttaa listan osoitteista)
def get_all_wallets() -> list:
    return list(wallets.keys())

# Funktio lompakon poistamiseen (tarkistaa olemassaolon)
def remove_wallet(address: str):
    if address not in wallets:
        raise ValueError("Lompakkoa ei löydy listalta.")
    
    del wallets[address]
    save_wallets()

# Funktio tokenin lisäämiseen (tarkistaa duplikaatit contractin perusteella)
def add_token(symbol: str, contract: str):
    # Tarkista onko sama contract jo lisätty (riippumatta symbolista)
    if any(c == contract for c in tokens.values()):
        raise ValueError("Token on jo lisätty (duplikaatti contract).")
    
    if symbol in tokens:
        raise ValueError("Token-symbol on jo käytössä.")
    
    tokens[symbol] = contract
    save_tokens()

# Funktio tokenin poistamiseen (tarkistaa contractin perusteella)
def remove_token(contract: str):
    # Etsi symbol contractin perusteella
    for sym, cont in list(tokens.items()):
        if cont == contract:
            del tokens[sym]
            save_tokens()
            return
    
    raise ValueError("Tokenia ei löydy listalta.")

# Funktio kaikkien tokenien hakemiseen (palauttaa dict symbol -> contract)
def get_all_tokens() -> dict:
    return tokens.copy()