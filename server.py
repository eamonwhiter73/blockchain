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

@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    pprint(last_block)

    print("last block")
    print("last block")
    print("last block")

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

    return sjson.dumps(response), 200

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
    #print(str(values['proof']) + " : proof")
    #required = ['proof']

    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    #proof = values['proof']

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

    print("\n //// REQUEST PRINTED - previous hash sent:\n")
    pprint(request.args)
    print("\n")
    var = request.args['previous']
    return_arr = []

    print("\n //// my_full_chain:\n")
    pprint(blockchain.chain)
    print("\n")

    for index, item in enumerate(blockchain.chain):
        print("\n //// ENUMERATING - from self blockchain:\n")
        pprint(item)
        print("\n")
        if item['previous_hash'] is {} and item['previous_hash'] == var:
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

@app.route('/previous', methods=['GET'])
def previous():

    return jsonify(blockchain.last_block['previous_hash']), 200

@app.route('/add_validated_block', methods=['POST'])
def add_validated_block():
    values = request.get_json()

    pprint(values)
    print("add validated block 77777777777777777")
    print("add validated block 77777777777777777")
    print("add validated block 77777777777777777")

    blockchain.add_validated_block(values)

    response = {
        'result': "block added"
    }

    return jsonify(result), 200

@app.route('/add_chain', methods=['POST'])
def add_chain():
    print("INSIDE ADD CHAIN PRINTING REQUESTS:")
    values = request.get_json()
    pprint(request.form)
    pprint(request.args)

    pprint(values)
    chain = values['chain']
    print("chain -----00--0------")
    print("chain -----00--0------")
    print("chain -----00--0------")

    if values['method'] == 'whole' and len(chain) > len(blockchain.chain):
        blockchain.chain =[]

    for index, item in enumerate(chain):
        blockchain.chain.append(item)

    response = {
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)