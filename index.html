# backend.py
from flask import Flask, jsonify, request, send_from_directory
from web3 import Web3
import os
from datetime import datetime
from dotenv import load_dotenv
import security
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import PublicFormat, Encoding
from cryptography.hazmat.backends import default_backend
from flask import send_file

load_dotenv()

app = Flask(__name__, static_folder='./', static_url_path='')

# Конфигурация
RPC_URL = os.getenv('RPC_URL', 'https://eth.llamarpc.com')
PORT = int(os.getenv('PORT', 3000))
HSM_LIB_PATH = os.getenv('HSM_LIB_PATH', '/usr/lib/hsm_lib.so')

w3 = Web3(Web3.HTTPProvider(RPC_URL))
hsm_client = security.HSMClient(HSM_LIB_PATH)

# Базы данных
transactions_db = []
wallet_balances = {}
mfa_handlers = {}
hsm_keys = {}

@app.route('/')
def serve_index():
    return send_file('index.html', mimetype='text/html')

# Генерация нового кошелька
@app.route('/api/wallet/new', methods=['POST'])
def create_wallet():
    data = request.json
    mnemonic = security.generate_bip39_mnemonic()
    seed = security.derive_seed(mnemonic, data.get('passphrase', ''))

    private_key = hsm_client.generate_key(f"key_{datetime.now().timestamp()}")
    public_key = private_key.public_key()

    # Генерация адреса Ethereum-стиля
    public_bytes = public_key.public_bytes(
        Encoding.X962,
        PublicFormat.UncompressedPoint
    )
    keccak_hash = Web3.keccak(public_bytes[1:])  # Пропускаем заголовок
    address = '0x' + keccak_hash[-20:].hex()

    # Инициализация MFA
    mfa = security.MFAHandler()
    mfa_handlers[address] = mfa
    hsm_keys[address] = private_key

    return jsonify({
        'mnemonic': mnemonic,
        'address': address,
        'mfa_secret': mfa.secret,
        'mfa_uri': mfa.get_provisioning_uri(address)
    })


# Подписание транзакции
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


# Верификация транзакции
@app.route('/api/transaction/verify', methods=['POST'])
def verify_transaction():
    data = request.json
    public_key = serialization.load_pem_public_key(
        data['public_key'].encode(),
        backend=default_backend()
    )
    is_valid = security.verify_signature(
        public_key,
        bytes.fromhex(data['signature']),
        data['transaction'].encode()
    )
    return jsonify({'valid': is_valid})


# Холодное подписание
@app.route('/api/cold-storage/sign', methods=['POST'])
def cold_sign():
    data = request.json
    private_key = serialization.load_pem_private_key(
        data['private_key'].encode(),
        password=None,
        backend=default_backend()
    )
    signature = security.ColdStorage.sign_offline(
        private_key,
        data['transaction'].encode()
    )
    return jsonify({'signature': signature.hex()})


# Остальные маршруты из исходного файла
@app.route('/api/balance/<address>', methods=['GET'])
def get_balance(address):
    try:
        balance_wei = w3.eth.get_balance(address)
        balance_eth = w3.from_wei(balance_wei, 'ether')
        wallet_balances[address] = float(balance_eth)
        return jsonify({
            'address': address,
            'balance': float(balance_eth),
            'unit': 'ETH'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/transactions/<address>', methods=['GET'])
def get_transactions(address):
    try:
        user_transactions = [
            tx for tx in transactions_db
            if tx['from'].lower() == address.lower() or tx['to'].lower() == address.lower()
        ]
        return jsonify(user_transactions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    try:
        data = request.json
        required_fields = ['hash', 'from', 'to', 'amount']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        new_tx = {
            'hash': data['hash'],
            'from': data['from'],
            'to': data['to'],
            'amount': float(data['amount']),
            'timestamp': data.get('timestamp', datetime.utcnow().isoformat())
        }

        transactions_db.append(new_tx)

        # Обновляем кэш балансов
        if new_tx['from'] in wallet_balances:
            wallet_balances[new_tx['from']] -= new_tx['amount']
        if new_tx['to'] in wallet_balances:
            wallet_balances[new_tx['to']] += new_tx['amount']

        return jsonify(new_tx), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(port=PORT)