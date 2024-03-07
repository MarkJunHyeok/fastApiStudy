from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from config.conection import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(256), nullable=False)
    password = Column(String(256), nullable=False)
    todos = relationship("ToDo", lazy="joined")

    @classmethod
    def create(cls, username: str, password: str) -> "User":
        return cls(username=username, password=password)
