import { useState } from 'react';
import { ethers } from 'ethers';

function App() {
  // Состояния кошелька
  const [walletAddress, setWalletAddress] = useState('');
  const [balance, setBalance] = useState('');
  
  // Состояния транзакции
  const [recipient, setRecipient] = useState('');
  const [amount, setAmount] = useState('');
  const [txStatus, setTxStatus] = useState('');
  
  // История транзакций
  const [transactions, setTransactions] = useState([]);

  // 1. Создание/подключение кошелька
  const createWallet = async () => {
    const wallet = ethers.Wallet.createRandom();
    setWalletAddress(wallet.address);
    setBalance('0.0 ETH');
    setTxStatus('Новый кошелёк создан!');
  };

  const connectWallet = async () => {
    if (!window.ethereum) {
      setTxStatus('Error: Установите MetaMask');
      return;
    }

    try {
      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const address = await signer.getAddress();
      setWalletAddress(address);
      
      const balance = await provider.getBalance(address);
      setBalance(ethers.formatEther(balance) + ' ETH');
      setTxStatus('Кошелёк подключен!');
    } catch (error) {
      setTxStatus(`Error: ${error.message}`);
    }
  };

  // 2. Отправка транзакции
  const sendTransaction = async () => {
    if (!window.ethereum) {
      setTxStatus('Error: MetaMask не установлен');
      return;
    }

    if (!recipient || !amount) {
      setTxStatus('Error: Заполните все поля');
      return;
    }

    try {
      setTxStatus('Обработка транзакции...');
      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      
      const tx = await signer.sendTransaction({
        to: recipient,
        value: ethers.parseEther(amount)
      });
      
      setTxStatus(`Успех: ${tx.hash}`);
      setTransactions(prev => [...prev, {
        hash: tx.hash,
        to: recipient,
        amount: amount,
        timestamp: new Date().toLocaleString()
      }]);
      
      // Обновляем баланс
      const newBalance = await provider.getBalance(walletAddress);
      setBalance(ethers.formatEther(newBalance) + ' ETH');
      
      // Очищаем форму
      setRecipient('');
      setAmount('');
    } catch (error) {
      setTxStatus(`Ошибка: ${error.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4 md:p-8">
      <div className="max-w-md mx-auto bg-white rounded-xl shadow-md p-4 md:p-6">
        <h1 className="text-2xl font-bold mb-4">Ethereum Кошелёк</h1>
        
        {/* Блок кошелька */}
        {!walletAddress ? (
          <div className="space-y-4">
            <button
              onClick={createWallet}
              className="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
            >
              Создать кошелёк
            </button>
            <button
              onClick={connectWallet}
              className="w-full bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
            >
              Подключить MetaMask
            </button>
          </div>
        ) : (
          <div className="space-y-4 mb-6">
            <div>
              <p className="text-gray-600">Адрес:</p>
              <p className="font-mono break-all text-sm">{walletAddress}</p>
            </div>
            <div>
              <p className="text-gray-600">Баланс:</p>
              <p className="font-bold">{balance}</p>
            </div>
          </div>
        )}

        {/* Форма транзакции */}
        {walletAddress && (
          <div className="mt-6 space-y-4">
            <h2 className="text-xl font-semibold">Отправить ETH</h2>
            <div>
              <input
                type="text"
                placeholder="Адрес получателя (0x...)"
                className="w-full p-2 border rounded"
                value={recipient}
                onChange={(e) => setRecipient(e.target.value)}
              />
            </div>
            <div>
              <input
                type="number"
                placeholder="Сумма (ETH)"
                step="0.0001"
                min="0"
                className="w-full p-2 border rounded"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
              />
            </div>
            <button
              onClick={sendTransaction}
              className="w-full bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
              disabled={!recipient || !amount}
            >
              Отправить
            </button>
            {txStatus && (
              <p className={`text-sm ${
                txStatus.includes('Ошибка') ? 'text-red-500' : 
                txStatus.includes('Успех') ? 'text-green-500' : 
                'text-gray-500'
              }`}>
                {txStatus}
              </p>
            )}
          </div>
        )}

        {/* История транзакций */}
        {transactions.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold mb-4">История транзакций</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white border">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="py-2 px-4 border">Хеш</th>
                    <th className="py-2 px-4 border">Кому</th>
                    <th className="py-2 px-4 border">Сумма</th>
                    <th className="py-2 px-4 border">Дата</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((tx, index) => (
                    <tr key={index}>
                      <td className="py-2 px-4 border font-mono text-xs">
                        <a 
                          href={`https://etherscan.io/tx/${tx.hash}`} 
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-500 hover:underline"
                        >
                          {tx.hash.slice(0, 8)}...
                        </a>
                      </td>
                      <td className="py-2 px-4 border font-mono text-xs">
                        {tx.to.slice(0, 8)}...
                      </td>
                      <td className="py-2 px-4 border">{tx.amount} ETH</td>
                      <td className="py-2 px-4 border text-sm">
                        {tx.timestamp}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;