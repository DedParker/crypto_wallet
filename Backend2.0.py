# backend.py
from flask import Flask, jsonify, request, send_from_directory
from web3 import Web3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='../frontend/dist')

# Конфигурация
RPC_URL = os.getenv('RPC_URL', 'https://eth.llamarpc.com')
PORT = int(os.getenv('PORT', 3000))

# Подключение к Ethereum ноде
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# "База данных" в памяти
transactions_db = []
wallet_balances = {}

@app.route('/api/balance/<address>', methods=['GET'])
def get_balance(address):
    """Получить баланс кошелька"""
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
    """Получить историю транзакций для адреса"""
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
    """Добавить транзакцию в историю"""
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
        
        # Обновляем балансы в нашей "базе данных"
        if new_tx['from'] in wallet_balances:
            wallet_balances[new_tx['from']] -= new_tx['amount']
        if new_tx['to'] in wallet_balances:
            wallet_balances[new_tx['to']] += new_tx['amount']
        
        return jsonify(new_tx), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/estimate-gas', methods=['POST'])
def estimate_gas():
    """Оценить стоимость газа для транзакции"""
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
    """Обслуживание фронтенд приложения"""
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(port=PORT)