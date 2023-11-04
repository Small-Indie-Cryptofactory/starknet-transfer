from starknet_py.contract import Contract

from data.config import logger, withdraw_token, wallet_min_balance_from, wallet_min_balance_to
from data.models import DEFAULT_TOKEN_ABI, TokenAmount
from utils.utils import get_explorer_hash_link, random_float


class WithdrawToken:

    def __init__(self, starknet_client, recipient_wallet):
        self.starknet_client = starknet_client
        self.recipient_wallet = recipient_wallet

    def _get_transfer_call(self, token_contract, token_balance):
        return token_contract.functions['transfer'].prepare(
            recipient=self.recipient_wallet,
            amount=token_balance.Wei
        )

    async def _get_overall_fee(self, *args):
        try:
            invoke_tx = await self.starknet_client.account.sign_invoke_transaction(
                calls=[*args],
                auto_estimate=True
            )
            estimated_fee = await self.starknet_client.account.client.estimate_fee(invoke_tx)
            overall_fee = estimated_fee.overall_fee
            return overall_fee * 3
        except Exception:
            return False

    async def token_withdraw(self):
        failed_text = f'Failed | {self.starknet_client.hex_address} | failed withdraw token'
        try:
            token_balance, decimal, token_name = await self.starknet_client.get_balance()
            if int(token_balance.Wei) == 0:
                return (f'Warning | {self.starknet_client.hex_address} | '
                        f'actual {token_name} balance: {token_balance.Ether}!')
            logger.info(f'{self.starknet_client.hex_address} | actual {token_name} balance: {token_balance.Ether}!')

            token_contract = Contract(
                address=withdraw_token,
                abi=DEFAULT_TOKEN_ABI,
                provider=self.starknet_client.account
            )

            wallet_min_balance = TokenAmount(amount=(random_float(from_=wallet_min_balance_from,
                                                                  to_=wallet_min_balance_to,
                                                                  step=0.00000001)), decimals=decimal)

            token_balance = TokenAmount(token_balance.Ether - wallet_min_balance.Ether, decimals=decimal)
            if float(token_balance.Wei) < 1:
                return (f'Warning | {self.starknet_client.hex_address} | actual {token_name} '
                        f'balance lower than wallet min. balance!')

            transfer_call = self._get_transfer_call(token_contract, token_balance)

            if token_name == 'Ether':
                overall_fee = TokenAmount(await self._get_overall_fee(transfer_call), decimals=decimal, wei=True)
                if overall_fee:
                    token_balance = TokenAmount(token_balance.Wei - overall_fee.Wei, decimals=decimal, wei=True)
                    if float(token_balance.Wei) < 1:
                        return (f'Warning | {self.starknet_client.hex_address} | actual {token_name} balance '
                                f'is too low to cover the transaction fee.')
                    transfer_call = self._get_transfer_call(token_contract, token_balance)
                else:
                    return f'{failed_text}: transaction failed due to the calculated fee.'

            action = (f'{self.starknet_client.hex_address} | starting withdraw {token_balance.Ether} {token_name} to '
                      f'{self.starknet_client.value_to_hex(self.recipient_wallet)}')
            logger.info(action)

            response = await self.starknet_client.account.execute(
                calls=[transfer_call],
                auto_estimate=True
            )
            tx_hash = self.starknet_client.value_to_hex(response.transaction_hash)
            tx_res = await self.starknet_client.account.client.wait_for_tx(
                response.transaction_hash
            )
            tx_status = tx_res.finality_status.value
            return f'{action} | tx: {get_explorer_hash_link(tx_hash)} | status: {tx_status}'

        except Exception as err:
            return f'{failed_text}: something went wrong: {err}'
