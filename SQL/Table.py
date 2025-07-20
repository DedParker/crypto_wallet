from typing import Annotated
from sqlalchemy import BigInteger, Text, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.dialects.postgresql import ARRAY, TEXT
from sqlalchemy import String, Integer, DateTime, Numeric, ForeignKey, func
from SQL.DataBase import Base

intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]

#Таблица пользователей
class Users(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    login: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    wallets: Mapped[list["Wallets"]] = relationship(back_populates="user")

#Таблица кошельков
class Wallets(Base):
    __tablename__ = "wallets"

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    address: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    balance_eth: Mapped[float] = mapped_column(Numeric(36, 18), default=0)

    user: Mapped["Users"] = relationship(back_populates="wallets")

    transactions: Mapped[list["Transactions"]] = relationship(back_populates="wallet")

#Таблица транзакций
class Transactions(Base):
    __tablename__ = "transactions"

    id: Mapped[intpk]
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id", ondelete="CASCADE"))
    tx_hash: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    recipient: Mapped[str] = mapped_column(String, nullable=False)
    amount_eth: Mapped[float] = mapped_column(Numeric(36, 18), nullable=False)

    wallet: Mapped["Wallets"] = relationship(back_populates="transactions")


# stx = Annotated[str, mapped_column(Text)]

# #таблица пользователей
# class Users(Base):
#     __tablename__ = "users"

#     id: Mapped[intpk]
#     login: Mapped[stx] = mapped_column(primary_key=True)
#     password: Mapped[stx]

# #Таблица кошельков
# class Wallets(Base):
#     __tablename__ = "wallets"

#     id: Mapped[intpk]
#     address: Mapped[str] = mapped_column(String, unique=True, nullable=False)
#     created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
#     balance_eth: Mapped[float] = mapped_column(Numeric(36, 18), default=0)
    
