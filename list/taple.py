from typing import Annotated
from datetime import datetime
from sqlalchemy import String, Numeric, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base

intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]

# Таблица кошельков
class Wallets(Base):
    __tablename__ = "wallets"

    id: Mapped[intpk]
    address: Mapped[str] = mapped_column(String(42), unique=True, nullable=False)
    balance_eth: Mapped[float] = mapped_column(Numeric(36, 18), default=0)

    transactions: Mapped[list["Transactions"]] = relationship(
        back_populates="wallet",
        cascade="all, delete-orphan"
    )

# Таблица транзакций
class Transactions(Base):
    __tablename__ = "transactions"

    id: Mapped[intpk]
    wallet_id: Mapped[int] = mapped_column(ForeignKey("wallets.id", ondelete="CASCADE"))
    tx_hash: Mapped[str] = mapped_column(String(66), unique=True, nullable=False)
    recipient: Mapped[str] = mapped_column(String(42), nullable=False)
    amount_eth: Mapped[float] = mapped_column(Numeric(36, 18), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    wallet: Mapped["Wallets"] = relationship(back_populates="transactions")
