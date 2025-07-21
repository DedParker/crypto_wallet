from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from database import sync_engine, sync_session_factory, Base
from taple import *
from sqlalchemy.orm import Session
from decimal import Decimal

#пересоздание таблиц
class SyncORM:
    @staticmethod
    def create_tables():
        try:
            with sync_engine.begin() as conn:
                Base.metadata.drop_all(bind=conn)
                Base.metadata.create_all(bind=conn)
        except Exception as e:
            print(e)


class Wallet:

#добавление кошелька
    @staticmethod
    def add_wallet(address: str, balance: float = 0.0):
        try:
            with sync_session_factory() as session:
                stmt = insert(Wallets).values(
                    address=address,
                    balance_eth=Decimal(str(balance))
                ).on_conflict_do_nothing(index_elements=["address"])
                session.execute(stmt)
                session.commit()
        except Exception as e:
            print(e)

#получение кошелька по адресу
    @staticmethod
    def get_wallet_by_address(address: str):
        try:
            with sync_session_factory() as session:
                wallet = session.execute(select(Wallets).where(Wallets.address == address)).scalar_one_or_none()
                if wallet:
                    return {
                        "address": wallet.address,
                        "balance_eth": float(wallet.balance_eth)
                    }
                return None
        except Exception as e:
            print(e)


#обновление баланса
    @staticmethod
    def update_balance(address: str, new_balance: float):
        try:
            with sync_session_factory() as session:
                wallet = session.execute(select(Wallets).where(Wallets.address == address)).scalar_one_or_none()
                if wallet:
                    wallet.balance_eth = new_balance
                    session.commit()
        except Exception as e:
            print(e)

#вывод всех кошельков
    @staticmethod
    def get_wallets():
        try:
            with sync_session_factory() as session:
                wallets = session.execute(select(Wallets)).scalars().all()
                return [{
                    "address": w.address,
                    "balance_eth": float(w.balance_eth)
                } for w in wallets]
        except Exception as e:
            print(e)


class Transaction:

#создание транзакции   
    @staticmethod
    def create_transaction(sender: str, recipient: str, amount: float, tx_hash: str):
        try:
            with sync_session_factory() as session:
                wallet = session.execute(select(Wallets).where(Wallets.address == sender)).scalar_one_or_none()
                if wallet:
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

#вывод всех транзкций
    @staticmethod
    def get_transactions(address: str):
        try:
            with sync_session_factory() as session:
                wallet = session.execute(select(Wallets).where(Wallets.address == address)).scalar_one_or_none()
                if wallet:
                    txs = session.execute(select(Transactions).where(Transactions.wallet_id == wallet.id)).scalars().all()
                    return [{
                        "tx_hash": tx.tx_hash,
                        "recipient": tx.recipient,
                        "amount_eth": float(tx.amount_eth)
                    } for tx in txs]
        except Exception as e:
            print(e)