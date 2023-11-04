from data.config import logger
from utils.utils import gas_price_value, sleep_delay
from client import StarknetClient
from tasks.withdraw_token import WithdrawToken


async def start_user_withdraw(user_action):
    with open('wallets.csv', 'r') as wallets_obj:
        all_wallets: list = [wallet.strip() for wallet in wallets_obj]
    all_wallets = all_wallets[1:]

    for num, wallet in enumerate(all_wallets, start=1):
        try:
            logger.info(f'{num}/{len(all_wallets)} wallets')

            wallet_info = wallet.split(',')
            if len(wallet_info) != 4:
                wallet_info.append('')
            async with StarknetClient(
                    account_address=int(wallet_info[0].strip(), 16),
                    private_key=int(wallet_info[1].strip(), 16),
                    proxy=wallet_info[3].strip()
            ) as starknet_client:
                await gas_price_value(starknet_client)
                status = await WithdrawToken(starknet_client, int(wallet_info[2].strip(), 16)).token_withdraw()
                if 'Failed' in status:
                    logger.error(status)
                    continue
                elif 'Warning' in status:
                    logger.error(status)
                    continue
                else:
                    logger.success(status)

                if num == len(all_wallets):
                    msg = f'Withdraw successfully completed with {len(all_wallets)} wallets'
                    logger.success(msg)
                    continue

                if user_action == '1':
                    await sleep_delay()
        except Exception as err:
            logger.error(err)
