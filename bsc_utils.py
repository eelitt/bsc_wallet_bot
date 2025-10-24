from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()  # Lataa .env-tiedosto moduulin käyttöön

# Yhdistä BSC-verkkoon
bsc_rpc_url = os.getenv('BSC_RPC_URL', 'https://bsc-dataseed.binance.org/')  # Default jos puuttuu
web3 = Web3(Web3.HTTPProvider(bsc_rpc_url))

# Standardi ERC-20 ABI tarvittaville funktioille (balanceOf, symbol, decimals)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    }
]

# Funktio validin BSC-osoitteen tarkistamiseen
def is_valid_address(address: str) -> bool:
    try:
        web3.to_checksum_address(address)
        return True
    except:
        return False

# Funktio checksum-muotoon normalisointiin
def to_checksum_address(address: str) -> str:
    return web3.to_checksum_address(address)

# Funktio tokenin symbolin ja decimalsin hakemiseen (validointiin add_token:ssa)
def get_token_symbol_and_decimals(contract: str) -> tuple:
    try:
        token_contract = web3.eth.contract(address=contract, abi=ERC20_ABI)
        
        symbol = token_contract.functions.symbol().call()
        decimals = token_contract.functions.decimals().call()
        
        if not symbol:
            raise ValueError("Ei saatu symbolia – ei validi ERC-20.")
        
        return symbol, decimals
    except Exception as e:
        raise ValueError(f"Virheellinen ERC-20 contract: {e}")

# Funktio balancejen hakemiseen (BNB + kaikki tallennetut tokenit)
def get_balances(address: str) -> dict:
    try:
        checksum_address = web3.to_checksum_address(address)
        balances = {}
        
        # Hae natiivi BNB-balance
        balance_wei = web3.eth.get_balance(checksum_address)
        balances['BNB'] = float(web3.from_wei(balance_wei, 'ether'))
        
        # Hae ERC-20 tokenit storagesta
        from storage import get_all_tokens  # Import täällä välttääksemme syklin
        all_tokens = get_all_tokens()
        for symbol, contract in all_tokens.items():
            try:
                token_contract = web3.eth.contract(address=contract, abi=ERC20_ABI)
                balance_raw = token_contract.functions.balanceOf(checksum_address).call()
                decimals = token_contract.functions.decimals().call()
                balances[symbol] = float(balance_raw / (10 ** decimals))
            except Exception as e:
                logger.error(f"Virhe tokenin {symbol} haussa: {e}")
                balances[symbol] = 0.0  # Aseta 0 jos virhe, mutta jatka
        
        return balances
    except Exception as e:
        raise RuntimeError(f"Virhe BSC-balance haussa: {e}")