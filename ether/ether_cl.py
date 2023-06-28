import decimal
from web3 import Web3
import requests
from loguru import logger
from config import *


NODE_URL = settings_json['node_url']


w3 = Web3(Web3.HTTPProvider(NODE_URL))


def get_prices(symbol):
    url = f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USDT'
    response = requests.get(url)

    try:
        result = [response.json()]
        price = result[0]['USDT']
    except Exception as error:
        logger.error(f'{error}. set price : 0')
        price = 0
    return float(price)


def get_wallet_balance(wallet: str):
    checksum_wallet = w3.to_checksum_address(wallet)
    balance = w3.eth.get_balance(checksum_wallet)
    token_price = get_prices('ETH')
    return f"ETH balance: {round(w3.from_wei(balance, 'ether'), 4)}\n" \
           f"USDT amount: {round(round(w3.from_wei(balance, 'ether'), 4)*decimal.Decimal(token_price), 2)}"


def get_balance_with_token(wallet: str, token_address: str):
    checksum_wallet = w3.to_checksum_address(wallet)
    token_contract = w3.eth.contract(token_address, abi=erc20_abi)
    token_name = token_contract.functions.symbol().call()
    token_balance = token_contract.functions.balanceOf(checksum_wallet).call()
    token_price = get_prices(token_name)
    decimals = token_contract.functions.decimals().call()
    return f'Amount of {token_name}: {round(token_balance / 10 ** decimals, 2)}\nUSDT amount:' \
           f' {round(token_balance / 10 ** decimals, 2)*token_price}'


