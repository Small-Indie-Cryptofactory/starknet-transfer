import os
import sys
from pathlib import Path
from loguru import logger

# System PATH (Windows/Linux/MacOS)
if getattr(sys, 'frozen', False):
    ROOT_DIR = Path(sys.executable).parent.absolute()
else:
    ROOT_DIR = Path(__file__).parent.parent.absolute()

# Starknet public/private RPC
STARKNET_RPC = 'https://starknet-mainnet.public.blastapi.io'

# Delay between actions (seconds)
delay_from = 300
delay_to = 600

# Max gas price
MAX_GAS_PRICE = 35

# Contract ABI
ABIS_DIR = os.path.join(ROOT_DIR, 'abis')
LOGGER_DIR = os.path.join(ROOT_DIR, 'debug.txt')

# logger
logger.add(LOGGER_DIR, format='{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}', level='DEBUG')

# withdraw token
withdraw_token = int('0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7', 16) # <--- ETH with example

# min balance
wallet_min_balance_from = 0
wallet_min_balance_to = 0
