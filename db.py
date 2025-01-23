from sqlalchemy import BIGINT, create_engine, ForeignKey
from sqlalchemy.orm import declarative_base, DeclarativeBase, Mapped, mapped_column, sessionmaker

engine = create_engine('postgresql+psycopg2://postgres:admin@localhost:5432/exam_db')

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    tg_id : Mapped['int'] = mapped_column(BIGINT , primary_key=True)
    first_name : Mapped['str'] = mapped_column()
    last_name : Mapped['str'] = mapped_column(nullable=True)
    username : Mapped['str'] = mapped_column(nullable=True)

class Data(Base):
    __tablename__ = "datas"
    id:Mapped[int]=mapped_column(primary_key=True, autoincrement=True)
    file_id:Mapped[str]
    user_id:Mapped[int]=mapped_column(BIGINT, ForeignKey("users.tg_id" , ondelete="CASCADE"))
    file_name:Mapped[str]=mapped_column(nullable=True)
    file_type:Mapped[str]=mapped_column(nullable=True)

Base.metadata.create_all(engine)

