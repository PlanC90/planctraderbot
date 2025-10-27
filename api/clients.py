from typing import Optional
from binance.client import Client


def make_client(api_key: str, api_secret: str, use_testnet: bool) -> Client:
    client = Client(api_key, api_secret, testnet=use_testnet)
    if use_testnet:
        client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi/v1'
    return client



