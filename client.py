from typing import Optional

import asyncio
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientHttpProxyError
from aiohttp_proxy import ProxyConnector
from starknet_py.contract import Contract
from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import KeyPair
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
from starknet_py.net.client_errors import ClientError
from aiohttp.client_exceptions import ClientConnectorError

from data.models import TokenAmount, DEFAULT_TOKEN_ABI, ConnectProxyError
from data.config import logger, STARKNET_RPC, withdraw_token


class StarknetClient:
    chain_id = StarknetChainId.MAINNET

    def __init__(self, private_key: int, account_address: int, proxy: str = '', check_proxy: bool = True):
        self.hex_address = self.value_to_hex(account_address)
        self.key_pair = KeyPair.from_private_key(private_key)
        self.signer = StarkCurveSigner(account_address, self.key_pair, StarknetClient.chain_id)
        self.chain_id = StarknetChainId.MAINNET
        self.starknet_client = None
        self.account = None
        self.session = None
        self.connector = None
        self.proxy = proxy
        self.check_proxy = check_proxy

        if self.proxy:
            try:
                if 'http' not in self.proxy:
                    self.proxy = f'http://{self.proxy}'

            except BaseException as err:
                raise ValueError(str(err))

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.proxy:
            await self.session.close()

    async def initialize(self):
        self.starknet_client, self.connector = await self.initialize_starknet_client()
        self.account = Account(
            address=int(self.hex_address, 16),
            client=self.starknet_client,
            key_pair=self.key_pair,
            chain=self.chain_id
        )

    async def get_my_ip(self, max_retries=10):
        for _ in (range(max_retries)):
            try:
                async with self.session.get("https://ipinfo.io/ip") as response:
                    return await response.text()
            except (ClientHttpProxyError, ClientConnectorError):
                await asyncio.sleep(1)
        await self.close()
        raise ConnectProxyError(f'Wallet {self.hex_address} | Error occurred while using the proxy {self.proxy}')

    async def initialize_starknet_client(self):
        if self.proxy:
            connector = self.get_session()
            self.session = ClientSession(connector=connector)
            if self.check_proxy:
                my_ip = await self.get_my_ip()
                msg = (f"Address {self.hex_address}. Current proxy: {self.proxy.split('@')[1].split(':')[0]}. "
                       f"Current IP is: {my_ip}")
                logger.info(msg)
            client = FullNodeClient(
                node_url=STARKNET_RPC,
                session=self.session
            )
            return client, self.session
        if not self.proxy:
            logger.info(f'Proxy not used.')
            client = FullNodeClient(node_url=STARKNET_RPC)
            return client, None

    async def close(self):
        await self.session.close()

    def get_session(self):
        if self.proxy:
            return ProxyConnector.from_url(self.proxy)
        return None

    @staticmethod
    def int_to_str(value):
        hex_val = hex(value)[2:]
        return bytes.fromhex(hex_val).decode('utf-8')

    async def get_decimals_and_name(self, token_address: int, max_retries=10) -> (int, str):
        contract = Contract(
            address=token_address,
            abi=DEFAULT_TOKEN_ABI,
            provider=self.account
        )
        for _ in range(max_retries):
            try:
                decimal = await contract.functions['decimals'].call()
                name = await contract.functions['name'].call()
                return int(decimal.decimals), str(self.int_to_str(name.name))
            except ClientError:
                logger.info(f"Retry {_ + 1}/{max_retries} due to get token decimal")
        raise ValueError('Failed to check decimals balance.')

    async def get_balance(self, token_address: int = withdraw_token, max_retries=10) -> (int, int):
        for _ in range(max_retries):
            try:
                decimal, name = await self.get_decimals_and_name(token_address)
                return TokenAmount(
                   amount=await self.account.get_balance(token_address=token_address, chain_id=StarknetChainId.MAINNET),
                   decimals=decimal,
                   wei=True
                ), decimal, name

            except (ClientError, ClientConnectorError):
                logger.info(f"Retry {_ + 1}/{max_retries} due to get ETH wallet balance")
        raise ValueError(f'{self.hex_address} | Failed to retrieve balance.')

    def value_to_hex(self, value=None) -> Optional[str]:
        if not value:
            return '0x{:064x}'.format(self.recipient_wallet)
        return '0x{:064x}'.format(value)
