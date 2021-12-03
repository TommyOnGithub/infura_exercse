#!/usr/bin/env python3
''' This script was developed by Thomas Barry for Diffuse's Junior
    Software Engineer application process. The goal is to display token
    balances for the four requested tokens and to find out the total
    value of each token in USDT if they were to be swapped through
    1inch exchange.

    Requires module web3.py.
'''
import os
import requests

from web3 import Web3


POLYGON_MAINNET = 'https://polygon-mainnet.infura.io/v3/'
ONEINCH = 'https://api.1inch.exchange/'
WALLET_ADDR = '0x008062acA356B5F93F2F14b71Fd73db91A606d0C'
SHI3LD_ADDR = '0xf239e69ce434c7fb408b05a0da416b14917d934e'
KOGE_ADDR = '0x13748d548D95D78a3c83fe3F32604B4796CFfa23'
PEAR_ADDR = '0xc8bcb58caEf1bE972C0B638B1dD8B0748Fdc8A44'
SING_ADDR = '0xCB898b0eFb084Df14dd8E018dA37B4d0f06aB26D'
USDT_ADDR = '0xc2132d05d31c914a87c6611c10748aeb04b58e8f'

def convert_bal(balance, decimals):
    ''' Convert the balance given to include the correct number of
        digits for 1inch API
    '''
    while len(balance) < decimals:
        balance = '0%s' % balance
    return balance

def convert_bal_erg(balance, decimals):
    ''' Convert the balance given so it becomes human-readable
    '''
    balance = convert_bal(balance, decimals)
    if len(balance) > decimals:
        balance = '%s.%s' % (balance[:-decimals], balance[-decimals:])
    else:
        return '0.%s' % balance
    return balance

# Get our Project ID from its environment variable
PROJECT_ID = os.environ.get('INFURA_PROJECT_ID')
ABI = None
abi_filename = 'eth_abi.json'
if not os.path.isfile(abi_filename):
    print('Missing eth_abi.json file! Exiting...')
    exit()
with open(abi_filename) as f:
    ABI = f.read()

print('Connecting Web3 interface...')
# Obtain Web3 connection to Polygon Mainnet via Infura
web3 = Web3(Web3.HTTPProvider(POLYGON_MAINNET + PROJECT_ID))
if web3.isConnected():
    print('Web3 is connected!')
    print('The latest block number is %s.' % web3.eth.blockNumber)
else:
    print('Web3 connection failed, make sure the INFURA_PROJECT_ID environment'
          'variable is set. Exiting...')
    exit()

# Read wallet balances for each token
addresses = [SHI3LD_ADDR, KOGE_ADDR, PEAR_ADDR, SING_ADDR]
tokens = {}
print('Reading token balances...')
for token_addr in addresses:
    tokens[token_addr] = {}

    # Get the token contract to call
    checksum_addr = Web3.toChecksumAddress(token_addr)
    contract = web3.eth.contract(address=checksum_addr, abi=ABI)

    # Save some data for later use
    symbol = contract.functions.symbol().call()
    tokens[token_addr]['symbol'] = symbol
    decimals = contract.functions.decimals().call()
    tokens[token_addr]['decimals'] = decimals
    balance = contract.functions.balanceOf(WALLET_ADDR).call()
    tokens[token_addr]['balance'] = balance
    bal_erg = convert_bal_erg(str(balance), decimals)
    print('The balance of %s at address %s is %s.'
          % (symbol, WALLET_ADDR, bal_erg))

# Get the value of each token in USDT
print('Getting USDT quote for tokens...')
for addr, token in tokens.items():
    # Normalize token amount value for 1inch API
    amount = convert_bal(str(token['balance']), token['decimals'])
    url = ('%sv4.0/137/quote?fromTokenAddress=%s&toTokenAddress=%s&amou'
           'nt=%s' % (ONEINCH, addr, USDT_ADDR, amount))
    res = requests.get(url)
    res_json = res.json()
    print('The USDT balance of token %s is %s.'
          % (token['symbol'], res_json['toTokenAmount']))
