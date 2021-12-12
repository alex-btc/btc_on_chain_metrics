# obter uma série temporal da quantidade de endereços com saldo maior do que zero.

import json
import subprocess
import os
from tqdm import tqdm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
%matplotlib

from logging import error
import bitcoinrpc.authproxy

class RPC:
  rpc = None
  def __init__(self, address = "localhost", port = 8332, username = "", password = "", cookie = "", timeout = 1000):

    if (username != "" and username != None) and (password != None and password != ""):
      conString = "http://%s:%s@%s:%s" % (username, password, address, port)
    elif (cookie != "" and cookie != None):
      conString = "http://%s@%s%s" % (cookie, address, port)
    else:
      raise error("Missign authentication method!")
    try:
      self.rpc = bitcoinrpc.authproxy.AuthServiceProxy(conString)
      self.getbestBlockhash()
    except ConnectionRefusedError:
      print ("Connection refused! Is your bitcoind running?")
      exit(1)
    except bitcoinrpc.authproxy.JSONRPCException:
      print("Authentication error. Check your credentials")
      exit(1)

  def getBlockchainInfo(self):
    try:
      return self.rpc.getblockchaininfo()
    except ConnectionRefusedError:
      print ("Connection refused! Is your bitcoind running?")
      exit(1)
    except bitcoinrpc.authproxy.JSONRPCException:
      print("Authentication error. Check your credentials")
      exit(1)

  def getbestBlockhash(self):
    try:
      return self.rpc.getbestblockhash()
    except ConnectionRefusedError:
      print ("Connection refused! Is your bitcoind running?")
      exit(1)
    except bitcoinrpc.authproxy.JSONRPCException:
      print("Authentication error. Check your credentials")
      exit(1)  
  
  def getBlock(self, blockHash):
    if blockHash == None or len(blockHash) != 64:
      raise error("Invalid block hash")
    try:
      return self.rpc.getblock(blockHash)
    except ConnectionRefusedError:
      print ("Connection refused! Is your bitcoind running?")
      exit(1)
    except bitcoinrpc.authproxy.JSONRPCException:
      print("Authentication error. Check your credentials")
      exit(1)  

  def getTransaction(self, transactionId):
    if transactionId == None or len (transactionId) != 64:
      raise error ("Invalida transaction Id")
    try:
      return self.rpc.getrawtransaction(transactionId, True)
    except ConnectionRefusedError:
      print ("Connection refused! Is your bitcoind running?")
      exit(1)
    except bitcoinrpc.authproxy.JSONRPCException:
      print("Authentication error. Check your credentials")
      exit(1)  

  def getBlockWithTransactions(self, blockHash):
    if blockHash == None or len(blockHash) != 64:
      raise error("Invalid block hash")
    try:
      return self.rpc.getblock(blockHash, 2)
    except ConnectionRefusedError:
      print ("Connection refused! Is your bitcoind running?")
      exit(1)
    except bitcoinrpc.authproxy.JSONRPCException:
      print("Authentication error. Check your credentials")
      exit(1)

  def getGenesis(self):
    try:
      return self.rpc.getblock(0)
    except ConnectionRefusedError:
      print ("Connection refused! Is your bitcoind running?")
      exit(1)
    except bitcoinrpc.authproxy.JSONRPCException:
      print("Authentication error. Check your credentials")
      exit(1)  

  def getBlockHashByHeight(self, height):
    if height < 0:
      raise error ("Invalid block height")
    try:
      return self.rpc.getblockhash(height)
    except ConnectionRefusedError:
      print ("Connection refused! Is your bitcoind running?")
      exit(1)
    except bitcoinrpc.authproxy.JSONRPCException:
      print("Authentication error. Check your credentials")
      exit(1)  
  
#   def batchCommands(self, commands: list[str]):
#     return self.rpc.batch_(commands)

def testRPC(username, password):
  rpc = RPC(username=username, password=password, port=8332, address="localhost")
  block = rpc.getbestBlockhash()
  print(rpc.getBlockWithTransactions(block))

#####

# altere aqui o rpcuser e rpcpassword do seu arquivo bitcoin.conf
username = 'XXXX'
password = 'XXXX'

rpc = RPC(username=username, password=password, port=8332, address="localhost")

# descobre o numero do ultimo bloco:
last_blockhash = rpc.getbestBlockhash()
last_block = rpc.getBlock(last_blockhash)['height']

threshold_min_btc = 0.000001
qtd_blocos_gravar = 10000

qty_non_zero_addresses_per_block = {}

addresses = {} # saldo de cada endereço, movimenta a cada bloco
last_moved = {} # bloco da ultima movimentacao de cada endereco
values = [] # valor de cada transacao, pra estatistica, soh pego dos outputs.
values_block = [] # bloco de cada transacao, pra estatistica, soh pego dos outputs.
timestamp = {} # unix timestamp de cada bloco

# debug:
# block = 123456
# block = 711907 # bloco pequeno, 92 txs
# block = 1
# final_block = 171 # hal finney tx was on block 170

initial_block = 1
initial_block = 180001 # recomecando, ultimo bloco foi o 180000
initial_block = 290000 # recomecando, ultimo bloco foi o 180000
# final_block = 1000
final_block = last_block # ateh o final

for block in tqdm(range(initial_block, final_block)):

    # reinicia a conexao:
    rpc = RPC(username=username, password=password, port=8332, address="localhost")

    # descobre o hash do bloco:
    blockhash = rpc.getBlockHashByHeight(block)

    # pega as transacoes do bloco:
    blockinfo = rpc.getBlockWithTransactions(blockhash)
    txs = blockinfo['tx']
    timestamp[block] = blockinfo['time']

    # for tx in txs:
    for tx in tqdm(txs):
        # soma saldo:
        for output in tx['vout']:
            if 'addresses' in output['scriptPubKey'].keys():
                address = output['scriptPubKey']['addresses'][0]
            else:
                address = output['scriptPubKey']['hex'] # nesse caso, armazeno a public key como se fosse o address, para outros tipos de transacao obsoletas, dos primeiros blocos.

            value_to_add = float(output['value'])
            if address in addresses.keys():
                addresses[address] = addresses[address] + value_to_add
            else:
                addresses[address] = value_to_add

            last_moved[address] = block # se bloco eh positivo, movimentacao foi credito no endereco.

            values.append(float(value_to_add))
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
                tx_temp = rpc.getTransaction(input)
                value_to_subtract = float(tx_temp['vout'][inputs[input]]['value']) # usa o index pra encontrar o output certo
                
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

    # deprecado, estava demorando muito, substitui por numpy abaixo, mas o melhor seria registrar direto em uma numpy array, nao em um dict (fica pro futuro):
    # addresses_df = pd.Series(addresses)
    # qty_non_zero_addresses_per_block[block] = len(addresses_df[addresses_df > threshold_min_btc])
    # del addresses_df

    addresses_array = np.fromiter(addresses.values(), dtype=float) # o mais rapido ateh agora
    qty_non_zero_addresses_per_block[block] = (addresses_array > threshold_min_btc).sum()
    del addresses_array

    # grava dados a cada qtd_blocos_gravar:
    if block % qtd_blocos_gravar == 0:
        # altere aqui o diretorio em que quer gravar os resultados:
        data_path = 'C:/code/btc_on_chain_metrics/output/'
        if not os.path.isdir(data_path): # se diretorio ainda nao existe:
          os.mkdir(data_path)
        pd.Series(addresses).to_csv(data_path + 'addresses.csv')
        pd.Series(qty_non_zero_addresses_per_block).to_csv(data_path + 'qty_non_zero_addresses_per_block.csv')
        pd.Series(values, index=values_block).to_csv(data_path + 'values.csv')
        pd.Series(last_moved).to_csv(data_path + 'last_moved.csv')
        pd.Series(timestamp).to_csv(data_path + 'timestamp.csv')
        # refaz a conexao, porque a gravacao dos dados acima pode demorar um pouco e aih a conexao cai.
        rpc = RPC(username=username, password=password, port=8332, address="localhost")

# dataframes:
addresses_df = pd.Series(addresses)
values_df = pd.Series(values, index=values_block).sort_values()
last_moved_df = pd.Series(last_moved)
timestamp_df = pd.Series(timestamp)

# plotting:
pd.Series(qty_non_zero_addresses_per_block).plot()

######################