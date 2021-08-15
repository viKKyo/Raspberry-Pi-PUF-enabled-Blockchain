import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4
import elGamal
import requests
from flask import Flask, jsonify, request, Response
from linetimer import CodeTimer
import numpy as np
from pypuf.simulation import ArbiterPUF
from pypuf.io import random_inputs

class Blockchain:
	def __init__(self):
		self.current_transactions = []
		self.chain = []
		self.nodes = set()
		self.challResp = []

		self.new_block(previous_hash='1')

	def register_node(self, address):
		parsed_url = urlparse(address)
		if parsed_url.netloc:
			self.nodes.add(parsed_url.netloc)
		elif parsed_url.path:
			self.nodes.add(parsed_url.path)
		else:
			raise ValueError('Invalid URL')


	def valid_chain(self, chain):
		last_block = chain[0]
		current_index = 1

		while current_index < len(chain):
			block = chain[current_index]
			print(f'{last_block}')
			print(f'{block}')
			print("\n-----------\n")

			last_block_hash = self.hash(last_block)
			if block['previous_hash'] != last_block_hash:
				return False

			last_block = block
			current_index += 1

		return True

	def resolve_conflicts(self):
		neighbours = self.nodes
		new_chain = None

		max_length = len(self.chain)

		for node in neighbours: 
			response = requests.get(f'http://{node}/chain')

			if response.status_code == 200:
				length = response.json()['length']
				chain = response.json()['chain']

				if length > max_length and self.valid_chain(chain):
					max_length = length
					new_chain = chain

		if new_chain:
			self.chain = new_chain
			return True

		return False

	def new_block(self, previous_hash):
		block = {
			'index': len(self.chain) + 1,
			'timestamp': time(),
			'transactions': self.current_transactions,
			'previous_hash': previous_hash or self.hash(self.chain[-1]),
		}

		self.current_transactions = []

		self.chain.append(block)
		return block

	def new_transaction(self, sender, recipient, amount):
		self.current_transactions.append({
			'sender': sender,
			'recipient': recipient,
			'amount': amount,
		})

		return self.last_block['index'] + 1

	@property
	def last_block(self):
		return self.chain[-1]

	@staticmethod
	def hash(block):
		block_string = json.dumps(block, sort_keys=True).encode()
		return hashlib.sha256(block_string).hexdigest()

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/pufcheck', methods=['GET'])
def pufCheck():
		ip_address = request.remote_addr + ':5000'
		response = requests.get(f'http://{ip_address}/sendAuthPair') 
		challengeCheck = response.json()[0]['challenge']
		responseCheck = response.json()[0]['response']
		for dictNum in range(len(blockchain.challResp)):
			if blockchain.challResp[dictNum]['node'] == ip_address and blockchain.challResp[dictNum]['challenge'] == challengeCheck and blockchain.challResp[dictNum]['response'] == responseCheck:
				return 'IP address with matching response & challenge pair found', 200
			else:
				continue
		return 'IP address with matching response & challenge pair not found.', 500

@app.route('/enroll', methods=['GET', 'POST'])
def enroll():
		neighbours = blockchain.nodes
		for node in neighbours:
			response = requests.get(f'http://{node}/get/challenge')
			if response.status_code == 200:
				challenge = response.json()['challenge']
				chalResponse = response.json()['response']
				blockchain.challResp.append({
					'node': node,
					'challenge': challenge,
					'response': chalResponse,
				})
				print(f'Enrollment of node {node} successful')
			else:
				print('Enrollment not successful')
		return '\nEnrollment completed.'

@app.route('/neighbours', methods=['GET'])
def neighbours():
	response = blockchain.nodes
	return jsonify(response), 200
"""
/////////
Below method is to view format and overall structure of the dictionary of challenges and responses contained within a list.
/////////
@app.route('/chalAndRes', methods=['GET']) #for testing challResp dictionary within list
def chalAndRes():
	response = blockchain.challResp
	#for index in range(len(blockchain.challResp))
	return jsonify(response), 200
"""	
@app.route('/get/challenge', methods=['GET'])
def get_challenge():
	choiceArr = np.array([1, -1])
	challengeArr = np.random.choice(choiceArr, size=(15, 64))
	puf = ArbiterPUF(n=64, seed=1)
	resToChallenge = puf.eval(challengeArr)
	resToChallengeList = resToChallenge.tolist()
	challengeArrList = challengeArr.tolist()
	response = {
		"challenge": challengeArrList,
		"response": resToChallengeList,	
	}
	return jsonify(response), 200
			

@app.route('/mine', methods=['GET'])
def mine():
	last_block = blockchain.last_block
 
	blockchain.new_transaction(
		sender="0",
		recipient=node_identifier,
		amount=1,
	)

	previous_hash = blockchain.hash(last_block)
	block = blockchain.new_block(previous_hash)

	response = {
		'message': "New Block Forged",
		'index': block['index'],
		'transactions': block['transactions'],
		'previous_hash': block['previous_hash'],
	}
	return jsonify(response), 200



@app.route('/transactions/new', methods=['POST'])
def new_transaction():
	values = request.get_json()

	required = ['sender', 'recipient', 'amount']
	if not all(k in values for k in required):
		return 'Missing values', 400

	index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

	response = {'message': f'Transaction will be added to Block {index}'}
	return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
	response = {
		'chain': blockchain.chain,
		'length': len(blockchain.chain),
	}
	return jsonify(response), 200

@app.route('/authchain', methods=['GET', 'POST'])
def authChain():
	blockchain.chain = request.json
	response = {
	  'message': 'Authoritative chain received.',
	  'chain' : blockchain.chain
	}
	return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
	values = request.get_json()

	nodes = values.get('nodes')
	if nodes is None:
		return "Error: Please supply a valid list of nodes", 400

	for node in nodes:
		blockchain.register_node(node)

	response = {
		'message': 'New nodes have been added',
		'total_nodes': list(blockchain.nodes),
	}
	return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
	replaced = blockchain.resolve_conflicts()
	neighbours = blockchain.nodes
	if replaced:
		response = {
			'message': 'Our chain was replaced',
			'new_chain': blockchain.chain
		}
		for node in neighbours:
			res = requests.post(f'http://{node}/authchain', json=blockchain.chain)
	else:
		response = {
			'message': 'Our chain is authoritative',
			'chain': blockchain.chain
		}
		for node in neighbours:
			res = requests.post(f'http://{node}/authchain', json=blockchain.chain)
	return jsonify(response), 200
	



if __name__ == '__main__':
	from argparse import ArgumentParser

	parser = ArgumentParser()
	parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
	args = parser.parse_args()
	port = args.port
	#app.debug = True
	app.run(host='0.0.0.0', port=port)
