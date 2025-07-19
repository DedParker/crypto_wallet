// backend.js
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { ethers } = require('ethers');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Serve frontend static files
app.use(express.static(path.join(__dirname, 'dist')));

// In-memory "database" for demo purposes
let transactionsDB = [];
let walletBalances = {};

// Initialize provider
const provider = new ethers.JsonRpcProvider(process.env.RPC_URL || 'https://eth.llamarpc.com');

// API Routes

// Get wallet balance
app.get('/api/balance/:address', async (req, res) => {
  try {
    const { address } = req.params;
    const balance = await provider.getBalance(address);
    const formattedBalance = ethers.formatEther(balance);
    
    walletBalances[address] = formattedBalance;
    
    res.json({ 
      address, 
      balance: formattedBalance,
      unit: 'ETH'
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get transaction history
app.get('/api/transactions/:address', async (req, res) => {
  try {
    const { address } = req.params;
    const userTransactions = transactionsDB.filter(
      tx => tx.from === address || tx.to === address
    );
    res.json(userTransactions);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Save transaction to history
app.post('/api/transactions', (req, res) => {
  try {
    const { hash, from, to, amount, timestamp } = req.body;
    
    if (!hash || !from || !to || !amount) {
      return res.status(400).json({ error: 'Missing required fields' });
    }
    
    const newTransaction = {
      hash,
      from,
      to,
      amount,
      timestamp: timestamp || new Date().toISOString()
    };
    
    transactionsDB.push(newTransaction);
    
    if (walletBalances[from]) {
      walletBalances[from] = (parseFloat(walletBalances[from]) - parseFloat(amount)).toString();
    }
    if (walletBalances[to]) {
      walletBalances[to] = (parseFloat(walletBalances[to]) + parseFloat(amount)).toString();
    }
    
    res.status(201).json(newTransaction);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Estimate gas for a transaction
app.post('/api/estimate-gas', async (req, res) => {
  try {
    const { from, to, value } = req.body;
    
    if (!from || !to || !value) {
      return res.status(400).json({ error: 'Missing required fields' });
    }
    
    const gasEstimate = await provider.estimateGas({
      from,
      to,
      value: ethers.parseEther(value.toString())
    });
    
    const gasPrice = await provider.getGasPrice();
    
    res.json({
      gasEstimate: gasEstimate.toString(),
      gasPrice: ethers.formatUnits(gasPrice, 'gwei'),
      estimatedCost: ethers.formatEther(gasEstimate * gasPrice)
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Serve frontend
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});