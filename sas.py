from SQL.Functions import SyncORM
from SQL.Functions import User
from SQL.Functions import Wallet
from SQL.Functions import Transaction
SyncORM.create_tables()
User.add_user('sas','123')
Wallet.add_wallet('sas','bit',12)
Transaction.create_transaction('bit','uww', 3, '456' )
s = Transaction.get_transactions('bit')
print(s)
p = Transaction.get_wallets('sas')
print(p)
Wallet.delete_wallet('bit')
print(Transaction.get_wallets('sas'))