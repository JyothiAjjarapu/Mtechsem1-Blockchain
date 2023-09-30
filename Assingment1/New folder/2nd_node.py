# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, request, jsonify
import requests
from uuid import uuid4
from urllib.parse import urlparse
import privpubkey as genkey
import mongodb
from bson import json_util

# Part 1 - Building a Blockchain

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.nodes = set()
        get_blockchain_copy = db1.print_data()
        
        if get_blockchain_copy == []:
            self.create_block(proof = 1, previous_hash = '0')
            
        else:
            self.chain = get_blockchain_copy
            
            
    def add_hashtotransaction(self,block):
        lst = []
        
        
        for i in block['transactions']:
            lst.append(self.hash(i))
        return lst
    
    
    
    def blockcreation(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'markel_root': "",
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        
        
        self.transactions = []
        
        # if number of transactions mod 2 is not 0 or equal to 1,then it is odd. so if it is odd,
        
        if len(block['transactions'])%2 == 1:
            # we add the last transaction so that the number becomes even
            # block['transactions'][-1]['amount']=0
            # block['transactions'].append(block['transactions'][-1])
            
            block['markel_root'] = get_merkelroot(block['transactions'],block['transactions'][-1])
       
        # if no. of transection is even
        else:
            block['markel_root'] = get_merkelroot(block['transactions'])
        
        block['transactions'].extend(self.add_hashtotransaction(block))
        self.chain.append(block)
        block['_id'] = block['index']
        db1.insert_into_database(block)
        self.updating_blockchain()
       
        return block

    
    def get_prev_block(self):
        return self.chain[-1]

#using proof of work consensus algorithm. We need to check the four zeroes at the beginning.
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    
    def is_blockchain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    
    
    def adding_a_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount': amount})
        previous_block = self.get_prev_block()
        return previous_block['index'] + 1
    
    
    def adding_a_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    
    #  updating the blockchain
    def updating_blockchain(self):
        self.chain = db1.print_data()
    
    
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
    
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False


# Part 2 - Mining our Blockchain

# To create a Web App, we need flask.
app = Flask(__name__)

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-', '')

# Keys for user, both public and private.. being taken from the privatepublickey file 
user_pub_key = genkey.privpub_keys()[0]
user_priv_key = genkey.privpub_keys()[1]

# database object, as we imported database file, where we r string our blockchain.
db1 = mongodb.DB()

# generating merkel root
def get_merkelroot(*args):
    s = ""
    # print(args)
    for arg in args:
        for i in arg:
            # print(i)
            s += json_util.dumps(i)
    return hashlib.sha256(s.encode()).hexdigest()



# Function to get the amount spent
def amount_spent(address):
    bal = 10
    for i in blockchain.chain:
        for j in i['transactions']:
           
            if type(j)==type(dict()) and j['sender'] == address:
                bal += float(j['amount'])
    return bal

#function to get the balance in the account
def get_balance(address):
    bal = 4000
    for i in blockchain.chain:
        for j in i['transactions']:
           
            if type(j)==type(dict()) and j['receiver'] == address:
                bal += float(j['amount'])
    print(bal ,amount_spent(address))
    return bal - amount_spent(address)



# Creating a Blockchain
blockchain = Blockchain()



# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_prev_block()
    previous_proof = previous_block['proof']
    
    proof = blockchain.proof_of_work(previous_proof)
    
    previous_hash = blockchain.hash(previous_block)
    
    blockchain.adding_a_transaction(sender = node_address, receiver = user_pub_key, amount = 1)
    block = blockchain.blockcreation(proof, previous_hash)
   
    response = {'Alert': 'Hurray, you have succesfully mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous hash': block['previous_hash'],
                'transaction': block['transactions']}
    return json.loads(json_util.dumps(response)), 200


# printing the Blockchain
@app.route('/get_blockchain', methods = ['GET'])
def get_blockchain():
    response = {'Blockchain': blockchain.chain,
                'length of the chain': len(blockchain.chain)}
    return json.loads(json_util.dumps(response)), 200


# Checking the validity of the chain
@app.route('/is_chainvalid', methods = ['GET'])
def is_chainvalid():
    is_valid = blockchain.is_blockchain_valid(blockchain.chain)
    if is_valid:
        response = {'Message': 'Working fine. The Blockchain is valid.'}
    else:
        response = {'Problem!! Not valid.'}
    return json.loads(json_util.dumps(response)), 200

# Adding a new transaction to the Blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements of the transaction are missing', 400
    if get_balance(json['sender']) >= float(json['amount']):
        index = blockchain.adding_a_transaction(json['sender'], json['receiver'], json['amount'])
        response = {'message': f'This transaction will be added to Block {index}'}
    else:
        response = {'message': 'This transaction can not be done, Insufficient Balance'}
    return response, 201

# Part 3 - Decentralizing our Blockchain

# Connecting new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.adding_a_node(node)
    response = {'message': 'All the nodes in the chain are now connected. The Blockchain now contains the following nodes:',
                'All_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                    'new chain': blockchain.chain}
    else:
        response = {'message': 'All Fine. The chain is the largest one.',
                    'actual chain': blockchain.chain}
    return json.loads(json_util.dumps(response)), 200

# getting balence
@app.route('/get_balance',methods=['POST'])
def get_wallet_balance():
    req_data = request.get_json()
    bal = get_balance(req_data['receiver'])
    return {
            'balance': bal,
            'user': req_data['receiver'],
            }
# Running the app
app.run(host = '0.0.0.0', port = 5001)