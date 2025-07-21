from flask import Flask, jsonify, request, send_from_directory
from web3 import Web3
import os
from datetime import datetime
from dotenv import load_dotenv
import security
from cryptography.hazmat.primitives.serialization import PublicFormat, Encoding
from flask import send_file

from database import sync_engine, Base
from functions import Wallet, Transaction
from taple import Wallets, Transactions

load_dotenv()

app = Flask(__name__, static_folder='./', static_url_path='')


RPC_URL = os.getenv('RPC_URL', 'https://eth.llamarpc.com')
PORT = int(os.getenv('PORT', 3000))
HSM_LIB_PATH = os.getenv('HSM_LIB_PATH', '/usr/lib/hsm_lib.so')

w3 = Web3(Web3.HTTPProvider(RPC_URL))
hsm_client = security.HSMClient(HSM_LIB_PATH)

Base.metadata.create_all(sync_engine)

mfa_handlers = {}
hsm_keys = {}

@app.route('/')
def serve_index():
    return send_file('index.html', mimetype='text/html')

#создаем новый кошелек
@app.route('/api/wallet/new', methods=['POST'])
def create_wallet():
    data = request.json
    mnemonic = security.generate_bip39_mnemonic()
    seed = security.derive_seed(mnemonic, '')

    private_key = hsm_client.generate_key(f"key_{datetime.now().timestamp()}")
    public_key = private_key.public_key()

    public_bytes = public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
    keccak_hash = Web3.keccak(public_bytes[1:])
    raw_address = '0x' + keccak_hash[-20:].hex()
    checksum_address = Web3.to_checksum_address(raw_address)

    mfa = security.MFAHandler()
    mfa_handlers[checksum_address] = mfa
    hsm_keys[checksum_address] = private_key

    initial_balance = float(data.get('balance', 0.0))
    Wallet.add_wallet(checksum_address, initial_balance)

    return jsonify({
        'mnemonic': mnemonic,
        'address': checksum_address,
        'mfa_secret': mfa.secret,
        'mfa_uri': mfa.get_provisioning_uri(checksum_address)
    })

#подписываем транзакцию
@app.route('/api/transaction/sign', methods=['POST'])
def sign_transaction():
    data = request.json
    address = data['address']
    tx_data = data['transaction'].encode()
    mfa_code = data['mfa_code']

    if not mfa_handlers[address].verify_totp(mfa_code):
        return jsonify({'error': 'Invalid MFA code'}), 401

    private_key = hsm_keys[address]
    signature = hsm_client.sign(private_key, tx_data)

    return jsonify({
        'signed_tx': signature.hex(),
        'public_key': private_key.public_key().public_bytes(
            Encoding.PEM,
            PublicFormat.SubjectPublicKeyInfo
        ).decode()
    })

#получаем баланс кошелька
@app.route('/api/balance/<address>', methods=['GET'])
def get_balance(address):
    try:
        wallet = Wallet.get_wallet_by_address(address)
        if not wallet:
            return jsonify({'error': 'Кошелёк не найден'}), 404

        return jsonify({
            'address': wallet['address'],
            'balance': wallet['balance_eth'],
            'unit': 'ETH'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#получаем список транзакций по адресу
@app.route('/api/transactions/<address>', methods=['GET'])
def get_transactions(address):
    try:
        txs = Transaction.get_transactions(address)
        return jsonify(txs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#добавляем новую транзакцию в бд
@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    try:
        data = request.json
        required_fields = ['hash', 'from', 'to', 'amount']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        Transaction.create_transaction(
            data['from'],
            data['to'],
            float(data['amount']),
            data['hash']
        )

        return jsonify(data), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#оцениваем стоимость газа 
@app.route('/api/estimate-gas', methods=['POST'])
def estimate_gas():
    try:
        data = request.json
        required_fields = ['from', 'to', 'value']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        tx = {
            'from': data['from'],
            'to': data['to'],
            'value': w3.to_wei(data['value'], 'ether')
        }

        gas_estimate = w3.eth.estimate_gas(tx)
        gas_price = w3.eth.gas_price
        estimated_cost = gas_estimate * gas_price

        return jsonify({
            'gasEstimate': str(gas_estimate),
            'gasPrice': str(w3.from_wei(gas_price, 'gwei')),
            'estimatedCost': str(w3.from_wei(estimated_cost, 'ether'))
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#отдаём статические файлы или index.html
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(port=PORT)
