from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

engine = create_engine("sqlite:///inventory.db")
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class ItemDB(Base):
    __tablename__ = "items"

    name: Mapped[str] = mapped_column(primary_key=True)
    price: Mapped[float]
    stock: Mapped[int]

Base.metadata.create_all(engine)