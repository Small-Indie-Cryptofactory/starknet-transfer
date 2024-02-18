import time
import random
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from typing import Optional, Union

import aiohttp
import asyncio
from tqdm import tqdm
from fake_useragent import UserAgent

from data.config import logger, MAX_GAS_PRICE, delay_from, delay_to


async def get_starknet_actual_gas_price(starknet_client, max_retries=10):
    user_agent = UserAgent().chrome
    url = 'https://alpha-mainnet.starknet.io/feeder_gateway/get_block?blockNumber=latest'
    headers = {
        'authority': 'alpha-mainnet.starknet.io',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'ru-RU,ru;q=0.7',
        'user-agent': user_agent,
    }

    for _ in range(max_retries):
        try:
            connector = starknet_client.get_session()
            async with aiohttp.ClientSession(connector=connector) as session:
                async with await session.get(
                        url=url,
                        headers=headers,
                        allow_redirects=True
                ) as r:
                    result = (await r.json())
                    # print(result)
                    # gas_price = float(int(result['strk_l1_gas_price'], 16) / 1e9)
                    gas_price = float(int(result['strk_l1_gas_price'], 16) / 1e9)
                    return gas_price
        except asyncio.exceptions.TimeoutError:
            logger.debug(f"Retry {_ + 1}/{max_retries} due to TimeoutError Starknet gas price")

    raise ConnectionError(f'Not possible receive actual gas_price')


async def gas_price_value(starknet_client):
    starknet_gas_price = await get_starknet_actual_gas_price(starknet_client)
    while starknet_gas_price > MAX_GAS_PRICE:
        msg = (f'Current gas price is too high! Starknet gas price: {starknet_gas_price} '
               f'> {MAX_GAS_PRICE}! Sleep 10 minutes...')
        logger.warning(msg)
        sleep_time = 600
        for _ in tqdm(range(sleep_time), desc='Sleeping: ', unit='SEC', colour='GREEN'):
            await asyncio.sleep(1)
        starknet_gas_price = await get_starknet_actual_gas_price(starknet_client)
    return


def unix_to_strtime(unix_time: Union[int, float, str] = None, utc_offset: Optional[int] = None,
                    time_format: str = '%d.%m.%Y %H:%M:%S') -> str:
    if not unix_time:
        unix_time = time.time()

    if isinstance(unix_time, str):
        unix_time = int(unix_time)

    if utc_offset is None:
        strtime = datetime.fromtimestamp(unix_time)
    elif utc_offset == 0:
        strtime = datetime.utcfromtimestamp(unix_time)
    else:
        strtime = datetime.utcfromtimestamp(unix_time).replace(tzinfo=timezone.utc).astimezone(
            tz=timezone(timedelta(seconds=utc_offset * 60 * 60)))

    return strtime.strftime(time_format)


async def sleep_delay():
    sleep_time = random.randint(delay_from, delay_to)
    next_action_time = int(time.time()) + int(sleep_time)
    msg = (f'I was sleep {sleep_time} second(s). The next closest action will '
           f'be performed at {unix_to_strtime(next_action_time)}')
    logger.debug(msg)
    for _ in tqdm(range(sleep_time), desc='Sleeping: ', unit='SEC', colour='GREEN'):
        await asyncio.sleep(1)


def get_explorer_hash_link(tx_hash: str):
    return f'https://starkscan.co/tx/{tx_hash}'


def random_float(from_: Union[int, float, str], to_: Union[int, float, str],
                 step: Optional[Union[int, float, str]] = None) -> float:
    if from_ == 0 and to_ == 0:
        return 0
    from_ = Decimal(str(from_))
    to_ = Decimal(str(to_))
    if not step:
        step = 1 / 10 ** (min(from_.as_tuple().exponent, to_.as_tuple().exponent) * -1)

    step = Decimal(str(step))
    rand_int = Decimal(str(random.randint(0, int((to_ - from_) / step))))
    return float(rand_int * step + from_)
