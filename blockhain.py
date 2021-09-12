import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, request
from flask.json import jsonify
from textwrap import dedent


class Blockchain():
    def __init__(self) -> None:
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash = 1, proof = 100)

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof


    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof, proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:3] == "000"


    def new_block(self, proof, previous_hash = None):
        block = {
            'index' : len(self.chain) + 1,
            'timestamp' : time(),
            'transactions' : self.current_transactions,
            'proof' : proof,
            'previous_hash' : previous_hash or self.hash(self.chain[-1])
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender' : sender,
            'recipient' : recipient,
            'amount' : amount
        })
        
        return self.last_block['index'] + 1

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append(
            {
                'sender' : sender,
                'recipient' : recipient,
                'amount' : amount,
            }
        )
        return self.last_block['index'] + 1

app = Flask(__name__)
#api = api(app)

node_indentifier = str(uuid4()).replace('-', '')

blockhain = Blockchain()

@app.route('/mine', methods = ['GET'])
def mine():
    last_block = blockhain.last_block
    last_proof = last_block['proof']
    proof = blockhain.proof_of_work(last_proof)
    blockhain.new_transaction(
        sender = 0,
        recipient = node_indentifier,
        amount = 1
    )

    previous_hash = blockhain.hash(last_block)
    block = blockhain.new_block(proof, previous_hash)

    response = {
        'message' : 'New Block is here!',
        'index' : block['index'],
        'transactions': block['transactions'],
        'proof' : block['proof'],
        'previous_hash' : block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods = ['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all (k in values for k in required):
        return 'Missing values', 400

    index = blockhain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message' : f'transaction will be added to Block {index}'}
    return jsonify(response), 201



@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockhain.chain,
        'length': len(blockhain.chain)
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5000)