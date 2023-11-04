#### Install required packages
```bash
sudo apt update && \
sudo apt install python3 wget git -y
```
#### Clone the repo
```
git clone https://github.com/saniksin/starknet-transfer
```
#### Install python packages with pip
```bash
cd $HOME/starknet-transfer && \
pip install -r requirements.txt
```
### Edit wallets.txt which is located in $HOME/starknet-transfer/wallets.txt 
#### Make it look like this (one wallet info = one line):

> Note: don't delete my_starknet_wallet, my_starknet_private_key, okx_deposit_wallet, proxy. Please make sure not to remove this line from the CSV file.

```
my_starknet_wallet, my_starknet_private_key, okx_deposit_wallet, proxy (not necessary)
0x..., 0x..., 0x...,              			# <---- without proxy
0x..., 0x..., 0x..., http://login:password@ip:port      # <---- with proxy (you can mix)
```
> Note: if you don't specify a proxy, the requests will be sent from a single IP, which is not highly recommended.
 
### Settings

Open data > config.py, you can adjust these settings:

- STARKNET_RPC - link to a public or private RPC. The minimum supported version should be 0.4.0.
- delay_from / delay_to - a random delay time between two values will be chosen. Specify an integer in seconds.
- MAX_GAS_PRICE - maximum gas price, above which the script will sleep.
- withdraw_token - token contract for withdrawal, can be replaced with any other. Defaults to ETH.
- wallet_min_balance_from/wallet_min_balance_to - minimum token balance that should remain in the wallet, a random value between two wallets will be chosen. You can specify 0 and 0.

### Run the script
```python
python3 $HOME/starknet-transfer/main.py
```
### Logs
You can view all logs in your console or in the **debug.txt** file.
