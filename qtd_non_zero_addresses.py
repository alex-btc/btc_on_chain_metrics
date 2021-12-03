# obter uma série temporal da quantidade de endereços com saldo maior do que zero.

import json
import subprocess
import os
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib

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
last_block = int(run(['-getinfo'])['blocks'])

threshold_min_btc = 0.000001
qtd_blocos_gravar = 10000

qty_non_zero_addresses_per_block = {}

addresses = {} # saldo de cada endereço, movimenta a cada bloco
last_moved = {} # bloco da ultima movimentacao de cada endereco
values = [] # valor de cada transacao, pra estatistica, soh pego dos outputs.
values_block = [] # bloco de cada transacao, pra estatistica, soh pego dos outputs.

# debug:
# block = 123456
# block = 711907 # bloco pequeno, 92 txs

# block = 1
# final_block = 171 # hal finney tx was on block 170

initial_block = 1
# initial_block = 129894
final_block = last_block # ateh o final


for block in tqdm(range(initial_block, final_block)):

    # descobre o hash do bloco:
    blockhash = run(['getblockstats',str(block)])['blockhash']

    # pega as transacoes do bloco:
    txs = run(['getblock', str(blockhash), '2'])['tx']

    for tx in txs:
        # soma saldo:
        for output in tx['vout']:
            if 'addresses' in output['scriptPubKey'].keys():
                address = output['scriptPubKey']['addresses'][0]
            # elif output['scriptPubKey']['type'] == 'pubkey': # tipo de transacao obsoleta, dos primeiros blocos.
            else:
                address = output['scriptPubKey']['hex'] # nesse caso, armazeno a public key como se fosse o address.

            value_to_add = output['value']
            if address in addresses.keys():
                addresses[address] = addresses[address] + value_to_add
            else:
                addresses[address] = value_to_add

            last_moved[address] = block # se bloco eh positivo, movimentacao foi credito no endereco.

            values.append(value_to_add)
            values_block.append(block)

        # diminui saldo:
        inputs = {}
        for input in tx['vin']:
            if 'coinbase' in input.keys(): # block reward, nao tem output previo:
                inputs['coinbase'] = 'coinbase'
            else:
                inputs[input['txid']] = input['vout'] # txid e o index dos outputs dela que gerou esse input
        
        for input in list(inputs.keys()):
            if inputs[input] != 'coinbase': # se eh transacao coinbase nao ha o que diminuir.
                tx_temp = run(['getrawtransaction', input, '1'])
                value_to_subtract = tx_temp['vout'][inputs[input]]['value'] # usa o index pra encontrar o output certo
                
                tipo_tx = tx_temp['vout'][inputs[input]]['scriptPubKey']['type']

                if (tipo_tx == 'pubkey') or (tipo_tx == 'nonstandard'): # tipo de txs obsoletas
                    address = tx_temp['vout'][inputs[input]]['scriptPubKey']['hex']
                else:
                    address = tx_temp['vout'][inputs[input]]['scriptPubKey']['addresses'][0]
                
                if address in addresses.keys():
                    addresses[address] = addresses[address] - value_to_subtract
                else:
                    addresses[address] = -value_to_subtract

                last_moved[address] = -block # se bloco eh negativo, movimentacao foi debito no endereco.
            
    addresses_df = pd.Series(addresses)
    qty_non_zero_addresses_per_block[block] = len(addresses_df[addresses_df > threshold_min_btc])

    # grava dados a cada qtd_blocos_gravar:

    if block % qtd_blocos_gravar == 0:
        data_path = 'C:/code/btc_on_chain_metrics/output/'
        addresses_df.to_csv(data_path + 'addresses.csv')
        pd.Series(qty_non_zero_addresses_per_block).to_csv(data_path + 'qty_non_zero_addresses_per_block.csv')
        pd.Series(values, index=values_block).to_csv(data_path + 'values.csv')
        pd.Series(last_moved).to_csv(data_path + 'last_moved.csv')

values_df = pd.Series(values, index=values_block).sort_values()
last_moved_df = pd.Series(last_moved)

pd.Series(qty_non_zero_addresses_per_block).plot()


######################


