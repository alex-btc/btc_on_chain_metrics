# obter uma série temporal da quantidade de endereços com saldo maior do que zero.

import json
import subprocess
import os

# substitua aqui com a pasta em que estah o seu bitcoin-cli:
os.chdir('C:/Program Files/Bitcoin/daemon/')

def run(command):
    try:
        result_process = subprocess.run(['bitcoin-cli'] + command, stdout=subprocess.PIPE)
    except FileNotFoundError:
        # result_process = subprocess.run(['docker', 'exec', 'bitcoin', 'bitcoin-cli'] + command, stdout=subprocess.PIPE)
        result_process = subprocess.run(['bitcoin-cli'] + command, stdout=subprocess.PIPE)
    return json.loads(result_process.stdout)

# descobre o numero do ultimo bloco:
blocks = int(run(['-getinfo'])['blocks'])


# debug: escreva um bloco especifico para testar:
block = 123456

# descobre o hash do bloco:
blockhash = run(['getblockstats',str(block)])['blockhash']

# pega as transacoes do bloco:
txs = run(['getblock', str(blockhash), '2'])['tx']

# para armazenar os enderecos:
addresses = {}

for tx in txs:
    for vout in tx['vout']:
        if 'addresses' in vout['scriptPubKey'].keys():
            addresses[vout['scriptPubKey']['addresses'][0]] = vout['value']

print(addresses)
# muito mais a desenvolver... HELP!
