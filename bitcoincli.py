from logging import error
import bitcoinrpc.authproxy

class RPC:
  rpc = None
  def __init__(self, address = "localhost", port = 8332, username = "", password = "", cookie = "", timeout = 1000):
    conString = ""

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
  def batchCommands(self, commands: list[str]):
    return self.rpc.batch_(commands)



def testRPC():
  rpc = RPC(username="XXX", password="XXX", port=8332, address="localhost")
  block = rpc.getbestBlockhash()
  print(rpc.getBlockWithTransactions(block))
