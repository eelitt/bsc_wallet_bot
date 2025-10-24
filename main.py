import logging
from telegram.ext import ApplicationBuilder, CommandHandler
import storage  # Moduuli tallennukselle
import bot_handlers  
from dotenv import load_dotenv  # Lisätty: Env-lataukseen (TELEGRAM_TOKEN jne.)

load_dotenv()  # Lataa .env-tiedosto käynnistyksessä (korvaa config.py:n)

# Aseta logging virheiden seurantaan
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Pääfunktio botin käynnistämiseen
def main() -> None:
    # Lataa lompakot ja tokenit tiedostosta käynnistyksessä
    try:
        storage.load_wallets()
        storage.load_tokens()
    except Exception as e:
        logger.error(f"Virhe latauksessa: {e}")
    
    # Rakenna botti .env:n TELEGRAM_TOKEN:lla
    from os import getenv  # Lisätty: Os.getenv käyttöön TOKEN:lle
    telegram_token = getenv('TELEGRAM_TOKEN')
    if not telegram_token:
        raise ValueError("TELEGRAM_TOKEN puuttuu .env:stä – botti ei voi käynnistyä.")
    
    application = ApplicationBuilder().token(telegram_token).post_init(bot_handlers.post_init).build()
    
    # Lisää handlerit komentoille (importattu bot_handlers.py:stä)
    application.add_handler(CommandHandler("help", bot_handlers.help_command))
    application.add_handler(CommandHandler("addwallet", bot_handlers.addwallet_command))
    application.add_handler(CommandHandler("wallets", bot_handlers.wallets_command))
    application.add_handler(CommandHandler("removewallet", bot_handlers.removewallet_command))
    application.add_handler(CommandHandler("addtoken", bot_handlers.addtoken_command))
    application.add_handler(CommandHandler("calculate", bot_handlers.calculate_command))
    application.add_handler(CommandHandler("removetoken", bot_handlers.removetoken_command))
    application.add_handler(CommandHandler("tokens", bot_handlers.tokens_command))
    application.add_handler(CommandHandler("getid", bot_handlers.getid_command))
    
    # Käynnistä botti
    application.run_polling()

if __name__ == '__main__':
    main()