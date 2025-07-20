from sqlalchemy import select, delete, func
from sqlalchemy.dialects.postgresql import insert
from SQL.DataBase import sync_engine, sync_session_factory, Base
from SQL.Table import *
from sqlalchemy.orm import Session

class SyncORM:

# Создание новых таблиц
    @staticmethod
    def create_tables():
        try:
            with sync_engine.begin() as conn:
                Base.metadata.drop_all(bind=conn)
                Base.metadata.create_all(bind=conn)

        except Exception as e:
            print(e)

class User:

#Добавление пользователя
    def add_user(login: str, password: str):
        try:
            with sync_session_factory() as session:
                stmt = insert(Users).values(login=login, password=password).on_conflict_do_nothing(index_elements=["login"])
                session.execute(stmt)
                session.commit()
        except Exception as e:
            print(e)


#Удаление пользователя
    def delete_user(login: str):
        try:
            with sync_session_factory() as session:
                stmt = delete(Users).where(Users.login == login)
                session.execute(stmt)
                session.commit()
        except Exception as e:
            print(e)

class Wallet:
    
#Добавление кошелёка
    def add_wallet(login: str, address: str, balance: float = 0):
        try:
            with sync_session_factory() as session:
                user = session.execute(select(Users).where(Users.login == login)).scalar_one_or_none()
                stmt = insert(Wallets).values(user_id=user.id, address=address, balance_eth=balance).on_conflict_do_nothing(index_elements=["address"])
                session.execute(stmt)
                session.commit()
        except Exception as e:
            print(e)


#Удаление кошелька
    def delete_wallet(address: str):
        try:
            with sync_session_factory() as session:
                stmt = delete(Wallets).where(Wallets.address == address)
                session.execute(stmt)
                session.commit()
        except Exception as e:
            print(e)

class Transaction:

#Создание транзакций
    def create_transaction(address: str, recipient: str, amount: float, tx_hash: str):
        try:
            with sync_session_factory() as session:
                wallet = session.execute(select(Wallets).where(Wallets.address == address)).scalar_one_or_none()
                stmt = insert(Transactions).values(
                    wallet_id=wallet.id,
                    tx_hash=tx_hash,
                    recipient=recipient,
                    amount_eth=amount
                ).on_conflict_do_nothing(index_elements=["tx_hash"])
                session.execute(stmt)

                wallet.balance_eth -= amount
                session.commit()
        except Exception as e:
            print(e)


#Вывод всех кошельков с балансами
    def get_wallets(login: str):
        try:
            with sync_session_factory() as session:
                user = session.execute(select(Users).where(Users.login == login)).scalar_one_or_none()
                wallets = session.execute(select(Wallets).where(Wallets.user_id == user.id)).scalars().all()
                return [{
                    "address": w.address,
                    "balance_eth": float(w.balance_eth)
                } for w in wallets]
        except Exception as e:
            print(e)


#Вывод всех транзакций по кошельку
    def get_transactions(address: str):
        try:
            with sync_session_factory() as session:
                wallet = session.execute(select(Wallets).where(Wallets.address == address)).scalar_one_or_none()
                txs = session.execute(select(Transactions).where(Transactions.wallet_id == wallet.id)).scalars().all()
                return [{
                    "tx_hash": tx.tx_hash,
                    "recipient": tx.recipient,
                    "amount_eth": float(tx.amount_eth)
                } for tx in txs]
        except Exception as e:
            print(e)

# # Добавление  пользователя
#     @staticmethod
#     def add_user(login:str, password:str):
#         try:
#             with sync_session_factory() as session:
#                 stmt = insert(Users).values(login=login, password=password).on_conflict_do_nothing()
#                 session.execute(stmt)
#                 session.commit()

#         except Exception as e:
#             print(e)

# #Вывод всех пользователей
#     @staticmethod
#     def all_users():
#         try:
#             with sync_session_factory() as session:
#                 stmt = select(Users.login).order_by(Users.login)
#                 result = session.execute(stmt).scalars().all()  # список кортежей: [('title1', 'uid1'), ...]
#                 print(result)
#                 return result

#         except Exception as e:
#             print(e)
