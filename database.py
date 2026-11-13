import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# Read settings from .env (if it exists) into environment variables,
# so the password lives outside the code. Variables that are already set
# (for example by Docker Compose) are not overwritten.
load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL is not set. Copy .env.example to .env and fill it in.")

# create_engine does not connect yet; it only connects when a session first uses it.
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class ItemDB(Base):
    __tablename__ = "items"

    name: Mapped[str] = mapped_column(primary_key=True)
    price: Mapped[float]
    stock: Mapped[int]


def init_db():
    """Create any missing tables. Run once with `python database.py`, not on import."""
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
    print("Tables created (existing tables are left unchanged).")
