# bsc_wallet_bot

Kevyt BSC-wallet-botti telegrammiin

## Ominaisuudet
- Monitoroi annettujen BSC-lompakkojen balansseja
- Konfiguroitavat RPC-osoitteet ja ympäristömuuttujat.


## Vaatimukset
- Node.js 16+
- npm 


## Asennus
1. Kloonaa repo:
    ```
    git clone <repo-url>
    cd bsc_wallet_bot
    ```
2. Asenna riippuvuudet:
    ```
    npm install
    ```

## Konfigurointi
1. Aseta tarvittavat muuttujat .env tiedostoon
telegram chat id:n saa botin kautta. Botti päälle ja /getid

BSC_RPC_URL=https://bsc-dataseed.binance.org/
TELEGRAM_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=987654321

## Käyttö
Käynnistä botti:
```
npm start
```

## Lisenssi ja vastuuvapaus
Käytät omalla vastuulla.
