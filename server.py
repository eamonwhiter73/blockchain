from uuid import uuid4
from blockchain import Blockchain
from pprint import pprint
from flask import Flask, jsonify, request
import json
import simplejson as sjson

# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()
waiting = False

@app.route('/mine', methods=['GET'])
def mine():
    if not waiting:
        # We run the proof of work algorithm to get the next proof...
        last_block = blockchain.last_block
        print("\n Last_block:\n")
        pprint(last_block)
        #print("\n whole_chain:\n")
        #pprint(blockchain.chain)

        last_proof = last_block['proof']
        proof = blockchain.proof_of_work(last_proof)

        # We must receive a reward for finding the proof.
        # The sender is "0" to signify that this node has mined a new coin.
        blockchain.new_transaction(
            sender="0",
            recipient=node_identifier,
            amount=1,
        )

        # Forge the new Block by adding it to the chain
        previous_hash = blockchain.hash(last_block)
        block = blockchain.new_block(proof, previous_hash)

        response = { 'message': "New Block Forged",
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
            'node': node_identifier
        }

        return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/validate', methods=['GET']) # MIGHT MESS SOMETHING UP CHANGED FROM POST
def validate():
    
    proof = request.args.get('proof')

    last_block = blockchain.last_block
    last_proof = last_block['proof']

    if blockchain.valid_proof(last_proof, proof):
        response = { 'add': True }
    else:
        response = { 'add': False }

    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/chain_length', methods=['GET'])
def chain_length():
    response = {
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200

@app.route('/give_chain', methods=['GET'])
def give_chain():

    var = request.args.get('previous')
    return_arr = []

    for index, item in enumerate(blockchain.chain):
        if item['previous_hash'] == var:
            print("\n //// previous_hash is object and == request_previous_hash - getting chunk")
            return_arr = blockchain.chain[(index + 1):]
            method = 'partial'
        else:
            if index == (len(blockchain.chain) - 1):
                return_arr = blockchain.chain[:]
                print("\n //// Returning whole array below:\n")
                pprint(return_arr)
                print("\n")
                method = 'whole'

    response = {
        'chain': return_arr,
        'length': len(return_arr),
        'method': method
    }
    
    return jsonify(response), 200

@app.route('/start_mine', methods=['GET'])
def start_mine():

    waiting = False
    return jsonify({'message': 'mining started'}), 200

@app.route('/stop_mine', methods=['GET'])
def stop_mine():

    waiting = True
    return jsonify({'message': 'mining stopped'}), 200

@app.route('/previous', methods=['GET'])
def previous():

    return jsonify(blockchain.last_block['previous_hash']), 200

@app.route('/subtract_block', methods=['GET'])
def subtract_block():

    blockchain.subtract_block()

    response = {
        'result': "block removed"
    }

    return jsonify(response), 200

@app.route('/add_chain', methods=['POST'])
def add_chain():
    values = request.get_json()

    chain = values['chain']

    if values['method'] == 'whole' and len(chain) > len(blockchain.chain):
        blockchain.chain =[]

    for index, item in enumerate(chain):
        blockchain.chain.append(item)

    response = {
        'length': len(blockchain.chain),
        'message': 'chain added'
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)