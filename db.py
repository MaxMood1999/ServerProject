from sqlalchemy import BIGINT, create_engine
from sqlalchemy.orm import declarative_base, DeclarativeBase, Mapped, mapped_column


engine = create_engine('postgresql+psycopg2://postgres:1@m_pg:5432/postgres')
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    tg_id : Mapped['int'] = mapped_column(BIGINT , primary_key=True)
    first_name : Mapped['str'] = mapped_column()
    last_name : Mapped['str'] = mapped_column(nullable=True)
    username : Mapped['str'] = mapped_column(nullable=True)

Base.metadata.create_all(engine)

