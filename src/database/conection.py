from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'mysql+pymysql://root:todos@127.0.0.1:3306/todos'

engine = create_engine(DATABASE_URL)
SessionFactory = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()
