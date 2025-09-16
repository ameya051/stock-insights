from sqlalchemy import BigInteger, Column, Date, Numeric, String, TIMESTAMP, func, UniqueConstraint
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class EodPrice(Base):
    __tablename__ = "eod_prices"

    # Surrogate primary key
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Natural keys and data
    symbol = Column(String, nullable=False)
    trade_date = Column(Date, nullable=False, primary_key=True)
    open = Column(Numeric(20, 8), nullable=False)
    high = Column(Numeric(20, 8), nullable=False)
    low = Column(Numeric(20, 8), nullable=False)
    close = Column(Numeric(20, 8), nullable=False)
    vwap = Column(Numeric(20, 8))
    volume = Column(BigInteger)
    change_abs = Column(Numeric(20, 8))
    change_percent = Column(Numeric(14, 12))
    ingested_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

