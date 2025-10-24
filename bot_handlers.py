import logging
from telegram import Update
from telegram.ext import ContextTypes
import storage  # Moduuli tallennukselle
import bsc_utils  # Moduuli BSC-balance haulle
from dotenv import load_dotenv
import os 

load_dotenv()

logger = logging.getLogger(__name__)  # Logger handlerien virheille

# Käynnistymisviesti-callback: Lähetetään kun botti rakennetaan (post_init)
async def post_init(application) -> None:
    chat_id = os.getenv('CHAT_ID')
    if chat_id:
        try:
            await application.bot.send_message(chat_id=chat_id, text="Botti tulilla! /help näyttää komennot.")
        except Exception as e:
            logger.error(f"Virhe käynnistymisviestin lähettämisessä: {e}")
    else:
        logger.warning("CHAT_ID puuttuu .env:stä – käynnistymisviestiä ei lähetetä.")

# /help komento: Näyttää kaikki komennot ja niiden kuvaukset
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "/help - Näyttää tämän viestin\n"
        "/addwallet <osoite> - Lisää BSC-lompakon osoitteen listaan (tarkistaa olemassaolon)\n"
        "/wallets - Näyttää kaikki lompakot ja niiden balanssit\n"
        "/removewallet <osoite> - Poistaa lompakon listalta\n"
        "/addtoken <contract> - Lisää BSC-tokenin contract-osoitteen (tarkistaa validi ERC-20)\n"
        "/removetoken <contract> - Poistaa tokenin contract-osoitteen listalta\n"
        "/tokens - Näyttää kaikki tallennetut tokenit ja niiden contract-osoitteet\n"
        "/calculate - Laskee kaikkien lompakkojen token-balanssit yhteen\n"
        "/getid - Näyttää nykyisen chat_id:n (käytä .env:n asettamiseen)"
    )
    await update.message.reply_text(help_text)

# /addwallet komento: Lisää lompakon osoitteen
async def addwallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Käyttö: /addwallet <BSC-osoite>")
        return
    
    address = context.args[0]
    try:
        # Tarkista ja normalisoi osoite checksum-muotoon
        if not bsc_utils.is_valid_address(address):
            raise ValueError("Virheellinen BSC-osoite.")
        checksum_address = bsc_utils.to_checksum_address(address)
        
        storage.add_wallet(checksum_address)
        await update.message.reply_text(f"Lompakko {checksum_address} lisätty onnistuneesti.")
    except ValueError as e:
        await update.message.reply_text(str(e))
    except Exception as e:
        logger.error(f"Virhe lompakon lisäyksessä: {e}")
        await update.message.reply_text("Virhe lompakon lisäyksessä. Yritä uudelleen.")

# /wallets komento: Näyttää kaikki lompakot ja niiden balanssit
async def wallets_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        all_wallets = storage.get_all_wallets()
        if not all_wallets:
            await update.message.reply_text("Ei tallennettuja lompakoita.")
            return
        
        response = "Tallennetut lompakot ja balanssit:\n\n"
        for address in all_wallets:
            try:
                balances = bsc_utils.get_balances(address)
                response += f"Lompakko: {address}\n"
                for token, amount in balances.items():
                    response += f"- {token}: {amount:.4f}\n"
                response += "\n"
            except Exception as e:
                logger.error(f"Virhe balanssin haussa osoitteelle {address}: {e}")
                response += f"Lompakko: {address}\n- Balanssi: Ei saatavilla (virhe: {str(e)})\n\n"
        
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Virhe /wallets-komennossa: {e}")
        await update.message.reply_text("Virhe lompakkojen haussa. Yritä uudelleen.")

# /removewallet komento: Poistaa lompakon osoitteen
async def removewallet_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Käyttö: /removewallet <BSC-osoite>")
        return
    
    address = context.args[0]
    try:
        # Tarkista ja normalisoi osoite checksum-muotoon
        if not bsc_utils.is_valid_address(address):
            raise ValueError("Virheellinen BSC-osoite.")
        checksum_address = bsc_utils.to_checksum_address(address)
        
        storage.remove_wallet(checksum_address)
        await update.message.reply_text(f"Lompakko {checksum_address} poistettu onnistuneesti.")
    except ValueError as e:
        await update.message.reply_text(str(e))
    except Exception as e:
        logger.error(f"Virhe lompakon poistossa: {e}")
        await update.message.reply_text("Virhe lompakon poistossa. Yritä uudelleen.")

# /addtoken komento: Lisää tokenin contract-osoitteen
async def addtoken_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Käyttö: /addtoken <contract-osoite>")
        return
    
    contract = context.args[0]
    try:
        # Tarkista ja normalisoi contract checksum-muotoon
        if not bsc_utils.is_valid_address(contract):
            raise ValueError("Virheellinen contract-osoite.")
        checksum_contract = bsc_utils.to_checksum_address(contract)
        
        # Tarkista onko validi ERC-20 (hae symbol ja decimals)
        symbol, _ = bsc_utils.get_token_symbol_and_decimals(checksum_contract)
        
        storage.add_token(symbol, checksum_contract)
        await update.message.reply_text(f"Token {symbol} ({checksum_contract}) lisätty onnistuneesti.")
    except ValueError as e:
        await update.message.reply_text(str(e))
    except Exception as e:
        logger.error(f"Virhe tokenin lisäyksessä: {e}")
        await update.message.reply_text("Virhe tokenin lisäyksessä (ei validi ERC-20). Yritä uudelleen.")

# /calculate komento: Laskee kaikkien lompakkojen balanssit yhteen
async def calculate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        all_wallets = storage.get_all_wallets()
        if not all_wallets:
            await update.message.reply_text("Ei tallennettuja lompakoita – ei laskettavaa.")
            return
        
        # Alusta summat (BNB aina mukana, tokenit dynaamisesti)
        totals = {'BNB': 0.0}
        all_tokens = storage.get_all_tokens()
        for symbol in all_tokens:
            totals[symbol] = 0.0
        
        # Looppaa lompakot ja lisää summiin
        for address in all_wallets:
            try:
                balances = bsc_utils.get_balances(address)
                for token, amount in balances.items():
                    totals[token] += amount
            except Exception as e:
                logger.error(f"Virhe balanssin haussa osoitteelle {address} laskennassa: {e}")
                # Jatka muilla lompakoilla, älä lisää virheellistä
        
        # Muotoile vastaus allekkain
        response = "Tallennetuissa lompakoissa on yhteensä:\n"
        for token, total in totals.items():
            response += f"- {token}: {total:.4f}\n"
        
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Virhe /calculate-komennossa: {e}")
        await update.message.reply_text("Virhe laskennassa. Yritä uudelleen.")

# /removetoken komento: Poistaa tokenin contract-osoitteen
async def removetoken_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Käyttö: /removetoken <contract-osoite>")
        return
    
    contract = context.args[0]
    try:
        # Tarkista ja normalisoi contract checksum-muotoon
        if not bsc_utils.is_valid_address(contract):
            raise ValueError("Virheellinen contract-osoite.")
        checksum_contract = bsc_utils.to_checksum_address(contract)
        
        storage.remove_token(checksum_contract)
        await update.message.reply_text(f"Token ({checksum_contract}) poistettu onnistuneesti.")
    except ValueError as e:
        await update.message.reply_text(str(e))
    except Exception as e:
        logger.error(f"Virhe tokenin poistossa: {e}")
        await update.message.reply_text("Virhe tokenin poistossa. Yritä uudelleen.")

# /tokens komento: Näyttää kaikki tallennetut tokenit ja contractit
async def tokens_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        all_tokens = storage.get_all_tokens()
        if not all_tokens:
            await update.message.reply_text("Ei tallennettuja tokeneita.")
            return
        
        response = "Tallennetut tokenit:\n\n"
        for symbol, contract in all_tokens.items():
            response += f"- {symbol}: {contract}\n"
        
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Virhe /tokens-komennossa: {e}")
        await update.message.reply_text("Virhe tokenien haussa. Yritä uudelleen.")

# /getid komento: Näyttää nykyisen chat_id:n (apua CHAT_ID konfigurointiin)
async def getid_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Nykyinen chat_id: {chat_id}. Kopioi tämä .env:n CHAT_ID:ksi käynnistymis- ja sulkeutumisviestejä varten.")