from typing import Annotated
from sqlalchemy import BigInteger, Text, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ARRAY, TEXT
from sqlalchemy import String, Integer, DateTime, Numeric, func

from SQL.DataBase import Base

intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
# usid = Annotated[int, mapped_column(BigInteger, unique=True)]
stx = Annotated[str, mapped_column(Text)]

class Users(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    login: Mapped[stx] = mapped_column(primary_key=True)
    password: Mapped[stx]

class Wallets(Base):
    __tablename__ = "wallets"

    id: Mapped[intpk]
    address: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    balance_eth: Mapped[float] = mapped_column(Numeric(36, 18), default=0)
    
# class Videos(Base):
#     __tablename__ = "videos"

#     id: Mapped[intpk]
#     uid: Mapped[stx]
#     title: Mapped[stx]
#     description: Mapped[stx]
#     likes: Mapped[int] = mapped_column(server_default=text("0"))
#     dislikes: Mapped[int] = mapped_column(server_default=text("0"))




# class Admin(Base):
#     __tablename__ = "admins"

#     id: Mapped[intpk]
#     login: Mapped[stx] = mapped_column(primary_key=True)
#     password: Mapped[stx]

 
# class Admins(Base):
#     __tablename__ = "admins"

#     id: Mapped[intpk]
#     user_id: Mapped[usid]
#     position: Mapped[int] = mapped_column(server_default=text("0"))

# class DQ(Base):
#     __tablename__ = "download_queue"

#     id: Mapped[intpk]
#     file_id: Mapped[stx]
#     text: Mapped[str] = mapped_column(Text, nullable=True)
#     active: Mapped[bool] = mapped_column(Boolean, server_default="false")

# class Photos(Base):
#     __tablename__ = "photos"

#     id: Mapped[intpk]
#     file_id: Mapped[stx]
#     type: Mapped[stx] = mapped_column(server_default="sfw")
#     name: Mapped[stx] = mapped_column(server_default="noname")
#     physical: Mapped[stx] = mapped_column(server_default="none")